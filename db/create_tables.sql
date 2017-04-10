﻿SET search_path TO public;

CREATE TABLE Trader (
	t_id SERIAL PRIMARY KEY,
	username TEXT NOT NULL,
	salt TEXT NOT NULL,
	psw TEXT NOT NULL
);

CREATE TABLE Conversation (
	c_id SERIAL PRIMARY KEY,
	t_id1 SERIAL REFERENCES Trader(t_id),
	t_id2 SERIAL REFERENCES Trader(t_id),
	t1_key TEXT NOT NULL,
	t2_key TEXT NOT NULL,
	started_on TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE TABLE Message_Sent (
	ms_id SERIAL PRIMARY KEY,
	c_id SERIAL REFERENCES Conversation(c_id),
	t_id SERIAL REFERENCES Trader(t_id),
	msg_content BYTEA NOT NULL,
	time_sent TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE TABLE Message_Received (
	mr_id SERIAL PRIMARY KEY,
	c_id SERIAL REFERENCES Conversation(c_id),
	t_id SERIAL REFERENCES Trader(t_id),
	msg_content BYTEA NOT NULL,
	time_received TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE TABLE Request (
	r_id SERIAL PRIMARY KEY,
	sender_id SERIAL REFERENCES Trader(t_id),
	receiver_id SERIAL REFERENCES Trader(t_id),
	sender_key TEXT NOT NULL,
	time_sent TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc'),
	status INTEGER DEFAULT 0
)
