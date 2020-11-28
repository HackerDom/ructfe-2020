
create table if not exists public.users(
login varchar not null unique,
password_hash varchar not null,
public_key varchar not null,
credit_card_credentials varchar not null); <--it is a place for flag for auth vuln, if we will create it

create table if not exists public.transactions(
id varchar not null unique,
login varchar not null,
encrypted_data varchar not null);