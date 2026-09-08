-- Nexus Edge staging database dump
-- generated 2026-08-15 by cron backup (DO NOT LEAVE IN WEBROOT)

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `email` varchar(128) NOT NULL,
  `password_md5` char(32) NOT NULL,   -- unsalted MD5 (crackable)
  `role` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
);

INSERT INTO `users` VALUES
(1,'admin','admin@nexus-core.local','21232f297a57a5a743894a0e4a801fc3','admin'),
(2,'j.smith','j.smith@nexus-core.local','5f4dcc3b5aa765d61d8327deb882cf99','user'),
(3,'backup_svc','backup@nexus-core.local','e10adc3949ba59abbe56e057f20f883e','service');

-- leak marker: IAW301{sql_dump_unsalted_md5_hashes_leaked}
