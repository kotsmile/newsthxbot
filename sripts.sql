select * from suggested_news;

drop table news;
drop table temp_news;
drop table users;
drop table suggested_news;

delete from users;

create table news
(
    id          INTEGER
        primary key autoincrement,
    source      TEXT not null,
    title       TEXT not null,
    link        TEXT not null
        unique,
    img_link     TEXT not null,
    description TEXT not null,
    pub_date     TEXT not null,
    is_new integer default 1
);

create table temp_news
(
    source      TEXT,
    title       TEXT,
    link        TEXT,
    img_link     TEXT,
    description TEXT,
    pub_date     TEXT
);

create table users
(
    id TEXT
        primary key,
    rated INTEGER default 0,
    is_new INTEGER default 1,
    is_admin INTEGER default 0
);

create table suggested_news (
    user_id INTEGER,
    news_id INTEGER,
    timestamp TEXT,
    score  INTEGER default 0,
    seen INTEGER default 0

);
-- select datetime('now')
update news set is_new = 0 where link not in (select link from temp_news);

insert into users (id, is_admin) values ('182301431', 1)

select * from users;

select * from news
where
(news.id not in (select news_id from suggested_news where user_id = '182301431'))
and
is_new = 1

select * from suggested_news;

insert into suggested_news (user_id, news_id, timestamp) values ('182301431', 4, datetime('now'))


select news_id from suggested_news where user_id = '182301431' and seen = 0 order by timestamp desc  limit 1

select * from users;
update users set notify = 0 where id != '182301431';

update users set is_admin = 1 where id = '182301431';

ALTER TABLE users
ADD notify INTEGER default 1;

update users set rated = rated + 1 where id = '182301431';

select count(*) from users