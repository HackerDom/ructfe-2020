create table if not exists public.users(
timestamp timestamp NOT NULL DEFAULT NOW(),
login varchar not null unique,
password_hash varchar not null,
public_key varchar not null,
credit_card_credentials varchar not null, --it is a place for flag for auth vuln, if we will create it
balance int not null,
cookie bytea not null); 

create table if not exists public.transactions(
timestamp timestamp NOT NULL DEFAULT NOW(),
id varchar not null unique,
login_from varchar not null,
encrypted_data varchar not null,
status_id int not null);

create table if not exists public.status(
id int not null unique,
name varchar not null);

CREATE FUNCTION delete_old_users() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  DELETE FROM public.users WHERE timestamp < NOW() - INTERVAL '1 seconds'; --change to max checker period
  RETURN NULL;
END;
$$;

CREATE TRIGGER delete_old_users_trigger
    AFTER INSERT ON public.users FOR EACH ROW
    EXECUTE PROCEDURE delete_old_users();