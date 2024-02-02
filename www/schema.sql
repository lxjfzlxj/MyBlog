drop database if exists myblog;

create database myblog;

use myblog;

create table users (
    `id` varchar(50) not null,
	`username` varchar(50) not null,
	`password` varchar(50) not null,
	`admin` boolean not null,
    `email` varchar(50) not null,
    `image` varchar(500) not null,
    `create_time` real not null,
    unique key `idx_email` (`email`),
    key `idx_create_time` (`create_time`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table blogs (
    `id` varchar(50) not null,
    `userid` varchar(50) not null,
    `username` varchar(50) not null,
    `userimage` varchar(500) not null,
    `title` varchar(50) not null,
    `content` text not null,
    `create_time` real not null,
    key `idx_create_time` (`create_time`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table comments (
    `id` varchar(50) not null,
    `blogid` varchar(50) not null,
    `userid` varchar(50) not null,
    `username` varchar(50) not null,
    `userimage` varchar(500) not null,
    `content` mediumtext not null,
    `create_time` real not null,
    key `idx_create_time` (`create_time`),
    primary key (`id`)
) engine=innodb default charset=utf8;