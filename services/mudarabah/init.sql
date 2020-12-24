create table if not exists public.users(
timestamp timestamp NOT NULL DEFAULT NOW(),
login varchar not null unique,
password_hash varchar not null,
private_key bytea not null,
credit_card_credentials varchar not null,
balance int not null,
cookie varchar not null); 

CREATE FUNCTION delete_old_users() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  DELETE FROM public.users WHERE timestamp < NOW() - INTERVAL '20 minutes';
  RETURN NULL;
END;
$$;

CREATE TRIGGER delete_old_users_trigger
    AFTER INSERT ON public.users FOR EACH ROW
    EXECUTE PROCEDURE delete_old_users();

create table if not exists public.transactions(
timestamp timestamp NOT NULL DEFAULT NOW(),
login_from varchar not null,
login_to varchar not null,
amount int not null,
description bytea not null);

CREATE FUNCTION delete_old_transactions() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  DELETE FROM public.transactions WHERE timestamp < NOW() - INTERVAL '20 minutes';
  RETURN NULL;
END;
$$;

CREATE TRIGGER delete_old_transactions_trigger
    AFTER INSERT ON public.transactions FOR EACH ROW
    EXECUTE PROCEDURE delete_old_transactions();