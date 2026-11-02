import streamlit as st
import psycopg
from psycopg.rows import dict_row
from streamlit.errors import StreamlitSecretNotFoundError


st.set_page_config(page_title="Animal records", page_icon=":material/pets:")
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("login_error", False)


def log_in() -> None:
    is_valid_login = (
        st.session_state["username"] == "palla"
        and st.session_state["password"] == "palla123"
    )
    st.session_state["authenticated"] = is_valid_login
    st.session_state["login_error"] = not is_valid_login


def log_out() -> None:
    st.session_state["authenticated"] = False


def get_database_params() -> dict[str, str]:
    settings = st.secrets["database"]
    required_keys = ("host", "port", "dbname", "user", "password")
    missing_keys = [
        key
        for key in required_keys
        if not isinstance(settings.get(key), str) or not settings[key]
    ]
    if missing_keys:
        raise ValueError(
            "Add these settings to the [database] section in "
            f".streamlit/secrets.toml: {', '.join(missing_keys)}."
        )

    params = {key: settings[key] for key in required_keys}
    options = settings.get("options", "-c search_path=animal_mgmt,public")
    if not isinstance(options, str):
        raise ValueError("The database options setting must be a string.")
    params["options"] = options
    return params


@st.cache_data(ttl=60)
def load_animals() -> list[dict[str, object]]:
    with psycopg.connect(**get_database_params()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT animalid, animalname, speciestype, age
                FROM animals
                ORDER BY animalid
                """
            )
            return [dict(row) for row in cursor.fetchall()]


def insert_animal(name: str, species: str, age: int) -> None:
    with psycopg.connect(**get_database_params()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO animals (animalname, speciestype, age)
                VALUES (%s, %s, %s)
                """,
                (name, species, age),
            )


if st.session_state["authenticated"]:
    with st.sidebar:
        st.write("Signed in as **palla**")
        st.button("Log out", on_click=log_out)

if not st.session_state["authenticated"]:
    st.title("Animal species records")
    st.write("Log in to view the animal data.")

    with st.form("login_form"):
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.form_submit_button("Log in", on_click=log_in)

    if st.session_state["login_error"]:
        st.error("Incorrect username or password.")
    st.caption("Sample login only: username `palla`, password `palla123`.")
    st.stop()

try:
    animals = load_animals()
except StreamlitSecretNotFoundError:
    st.error(
        "Database settings are missing. Add a [database] section to "
        ".streamlit/secrets.toml before using the animal records app."
    )
    st.code(
        '[database]\nhost = "localhost"\nport = "5432"\n'
        'dbname = "postgres"\nuser = "postgres"\n'
        'password = "your-database-password"\n'
        'options = "-c search_path=animal_mgmt,public"',
        language="toml",
    )
    st.stop()
except (KeyError, ValueError) as error:
    st.error(f"Invalid database configuration: {error}")
    st.stop()
except psycopg.Error as error:
    st.error(f"Could not load animal records from PostgreSQL: {error}")
    st.stop()

st.title("Animal records")
st.write("Browse the animal records and add new animals to the collection.")

with st.expander("Add an animal"):
    with st.form("add_animal_form"):
        animal_name = st.text_input("Animal name", max_chars=100)
        species = st.text_input("Species", max_chars=100)
        age = st.number_input("Age (years)", min_value=0, step=1)
        submitted = st.form_submit_button("Add animal")

    if submitted:
        animal_name = animal_name.strip()
        species = species.strip()
        if not animal_name or not species:
            st.error("Enter both an animal name and a species.")
        else:
            try:
                insert_animal(animal_name, species, int(age))
            except StreamlitSecretNotFoundError:
                st.error("Database settings are missing; the animal was not added.")
            except (KeyError, ValueError) as error:
                st.error(f"Invalid database configuration: {error}")
            except psycopg.errors.UniqueViolation:
                st.error("An animal with that name already exists.")
            except psycopg.Error as error:
                st.error(f"Could not add the animal to PostgreSQL: {error}")
            else:
                load_animals.clear()
                try:
                    animals = load_animals()
                except psycopg.Error as error:
                    st.error(
                        f"Added {animal_name}, but could not refresh the records: "
                        f"{error}"
                    )
                    st.stop()
                st.success(f"Added {animal_name} to the animal records.")

display_animals = [
    {
        "Animal ID": animal["animalid"],
        "Animal name": animal["animalname"],
        "Species": animal["speciestype"],
        "Age": animal["age"],
    }
    for animal in animals
]

species_options = ["All species"] + sorted(
    {str(animal["Species"]) for animal in display_animals}
)
selected_species = st.selectbox("Filter by species", species_options)

visible_animals = [
    animal
    for animal in display_animals
    if selected_species == "All species" or animal["Species"] == selected_species
]

total_animals, total_species = st.columns(2)
total_animals.metric("Animals shown", len(visible_animals))
total_species.metric(
    "Species in collection",
    len({animal["Species"] for animal in display_animals}),
)

st.dataframe(
    visible_animals,
    hide_index=True,
    alt="Animal records showing each animal's name, species, and age",
)