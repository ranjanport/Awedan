create database awedan;

CREATE SCHEMA awedan_v1;

CREATE TABLE IF NOT EXISTS awedan_v1.users
(
    id serial,
    username character varying(20) COLLATE pg_catalog."default",
    email character varying(50) COLLATE pg_catalog."default" NOT NULL,
    fname character varying(30) COLLATE pg_catalog."default",
    lname character varying(30) COLLATE pg_catalog."default",
    fullname character varying(60) COLLATE pg_catalog."default" GENERATED ALWAYS AS ((((fname)::text || ' '::text) || (lname)::text)) STORED,
    eid bigint,
    grp "char" NOT NULL DEFAULT 'S'::"char",
    passwd text NOT NULL,
    created_at timestamp with time zone DEFAULT '2023-12-30 08:12:53.13873+00'::timestamp with time zone,
    updated_at timestamp with time zone DEFAULT '2023-12-30 08:12:53.13873+00'::timestamp with time zone,
    is_verified boolean NOT NULL DEFAULT 'false',
    v_token character varying(500) COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (id, email)
);

-- Table: credentials.applications

-- DROP TABLE IF EXISTS credentials.applications;

CREATE TABLE IF NOT EXISTS awedan_v1.applications
(
    id character varying(100) COLLATE pg_catalog."default" NOT NULL GENERATED ALWAYS AS (((('UNI/'::text || (application_type)::text) || (college_code)::text) || (app_id)::text)) STORED,
    app_id serial NOT NULL ,
    sub character varying(300) COLLATE pg_catalog."default" NOT NULL,
    application_date timestamp without time zone NOT NULL DEFAULT '2023-12-30 09:22:13.649475'::timestamp without time zone,
    application_type "char" NOT NULL DEFAULT 'G'::"char",
    application_content text COLLATE pg_catalog."default" NOT NULL,
    application_status "char" DEFAULT 'D'::"char",
    college_code character varying(4) COLLATE pg_catalog."default" NOT NULL DEFAULT 'COLL'::character varying,
    resolution text COLLATE pg_catalog."default",
    resolution_date timestamp without time zone,
    last_updated timestamp without time zone NOT NULL,
    applicant_name character varying(60) COLLATE pg_catalog."default",
    applicant_enroll integer,
    applicant_mob integer,
    assigned_to integer,
    CONSTRAINT applications_pkey PRIMARY KEY (app_id, id)
);

select * from awedan_v1.users;
insert into awedan_v1.users (username, email, fname, lname, passwd, eid) values ('aman', 'aman.ranjan@mapmyindia.com', 'Aman', 'Ranjan', '4343dfsf', 43);
select * from awedan_v1.applications;
select * from awedan_v1.users where email='aman.ranjan@maspmyindia.com' or username='aa'
SELECT current_setting('TIMEZONE') AS timezone;



