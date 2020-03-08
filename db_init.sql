CREATE TABLE `transactions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `tx_id` varchar(255) NOT NULL,
  `from_account` varchar(255) NOT NULL,
  `to_account` varchar(255) NOT NULL,
  `amount` bigint(20) NOT NULL,
  `tx_time` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `from_account_balances` bigint(20) NOT NULL,
  `to_account_balances` bigint(20) NOT NULL,
  `pre_tx_id` varchar(255) NOT NULL,
  `from_account_sign` varchar(255) NOT NULL,
  `create_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `msg` json DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `tx_id_unique` (`tx_id`) USING BTREE,
  UNIQUE KEY `pre_tx_id_unique` (`pre_tx_id`) USING BTREE,
  KEY `sign_qunique` (`from_account_sign`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;