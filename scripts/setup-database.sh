create database nds_login_portal;

create schema credentials;

CREATE TABLE credentials.user_credentials
(
    id SERIAL NOT NULL,
    name text NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    uid text NOT NULL,
    role text,
    PRIMARY KEY (uid)
);

INSERT INTO credentials.user_credentials (id, name, username, password, uid, role) VALUES (1 ,'Aman', 'aman.ranjan@mapmyindia.com',  crypt('a', gen_salt('bf')), 'NDS-1', 'admin');