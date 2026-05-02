# ZTE ICE/KCP Session Timeline

This report is redacted and analysis-only. It does not contain packet replay code.

## Summary

- SPICE host: `2409:8c70:3a50:24f7::440`
- SPICE port: `5100`
- Proxy type: `ice`
- Secure proxy port: `60065`
- CAG endpoint: `36.133.100.80:8899`
- QUIC enabled: `0`
- proxy be_ssl: `1`
- kcp be_ssl: `1`
- TLS version: `TLS1.3`
- SPICE add_link events: `641`
- outband add_link events: `167`
- all channels connected: `True`
- ZTEC notify_quit seen: `True`

## Capture Filter

```tcpdump
(udp or tcp) and (host 36.133.100.80 or port 8899 or port 60065 or port 5100)
```

## Events

| Time | Source | Line | Category | Detail |
|---|---:|---:|---|---|
| `26-05-01 17:16:45.701` | `client.log.2` | 176 | `result` | [QTApplication][slotReceiveConnect                    : 127] suyan tcp Connect successfully! |
| `26-05-01 17:16:47.234` | `client.log.2` | 277 | `ice` | [QTApplication][initRedirectParams                    :9464] port[5100] proxy_port[] s_proxy_port[60065] proxy_type[ice], device_redirect_dest_port[5100]. |
| `26-05-01 17:16:47.255` | `client.log.2` | 330 | `session` | [QTApplication][session_connect                       :5869] session_connect before m_pHost[], m_pPort[5100] |
| `26-05-01 17:16:47.296` | `client.log.2` | 369 | `session` | [QTApplication][session_connect                       :5874] session_connect after m_pHost[2409:8c70:3a50:24f7::2aa], m_pPort[5100] |
| `26-05-01 17:16:47.300` | `client.log.2` | 397 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] main-1:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59883 |
| `26-05-01 17:16:47.300` | `client.log.2` | 404 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9226] [PROXY] Creating proxy fd session, fd_type_ex=6 |
| `26-05-01 17:16:47.300` | `client.log.2` | 405 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9246] [PROXY] Setting up spice proxy link with SSL=1 |
| `26-05-01 17:16:47.300` | `client.log.2` | 406 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9250] [PROXY] Creating UDP proxy fd session |
| `26-05-01 17:16:47.300` | `client.log.2` | 419 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9270] [PROXY] Assigning SPICE proxy socket |
| `26-05-01 17:16:47.300` | `client.log.2` | 420 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9277] [PROXY] Proxy fd session creation completed successfully |
| `26-05-01 17:16:47.301` | `client.log.2` | 421 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:47.301` | `client.log.2` | 427 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5704] [UDP] Successfully created UDT session for 36.133.100.80:8899 |
| `26-05-01 17:16:47.301` | `client.log.2` | 428 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5720] [SSL] Initializing SSL context for SPICE proxy |
| `26-05-01 17:16:47.304` | `client.log.2` | 429 | `ssl` | [GSpice       ][udt_init_ssl_ctx                      :5587] init SSL CTX for udt ok |
| `26-05-01 17:16:47.304` | `client.log.2` | 430 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5736] client is support quic:0 (proxy_sock->link_type:1 proxy_sock->be_ssl:1 kcp->be_ssl:1 kcp->be_multi:0 g_enable_udt_stream:0 pThread->enable_quic:0, proxy_sock->use_quic:0) |
| `26-05-01 17:16:47.317` | `client.log.2` | 434 | `kcp` | [GSpice       ][deal_kcp_auth_cmd                     :6439] kcp(syn_id = <redacted>, conv = <redacted>)recv IKCP_CONV_AUTH_HEAD_ACK from:36.133.100.80:8899 |
| `26-05-01 17:16:47.334` | `client.log.2` | 435 | `kcp` | [GSpice       ][deal_kcp_auth_cmd                     :6445] kcp(syn_id = <redacted>, conv = <redacted>) recv IKCP_CONV_AUTH_ACK from:36.133.100.80:8899 |
| `26-05-01 17:16:47.346` | `client.log.2` | 436 | `kcp` | [GSpice       ][deal_kcp_sync_ack_cmd                 :6603] kcp(syn_id=<redacted>, conv=<redacted>) recv IKCP_CONV_SYNACK from:36.133.100.80:8899 |
| `26-05-01 17:16:47.346` | `client.log.2` | 437 | `kcp` | [GSpice       ][deal_kcp_sync_ack_cmd                 :6604] kcp(syn_id=<redacted>, conv=<redacted>) be_quic=0 be_using_stream=0 be_ssl=1 |
| `26-05-01 17:16:47.346` | `client.log.2` | 438 | `ssl` | [GSpice       ][deal_kcp_sync_ack_cmd                 :6609] kcp(syn_id = <redacted>, conv = <redacted>) has not ssl connected, will try to connect... |
| `26-05-01 17:16:47.347` | `client.log.2` | 439 | `ssl` | [GSpice       ][check_ssl_connect_error               :6524] kcp(fd = 109 syn_id = <redacted>, conv = <redacted>) ssl connect failed, errno:2 |
| `26-05-01 17:16:47.347` | `client.log.2` | 440 | `ssl` | [GSpice       ][check_ssl_connect_error               :6527] fd session(fd = 109, type = 4, typeEx = 0) reset read/write function to handle ssl connect |
| `26-05-01 17:16:47.362` | `client.log.2` | 441 | `ssl` | [GSpice       ][deal_udt_ssl_connect                  :6516] SSL_connect connect and current version TLS1.3(0x304) |
| `26-05-01 17:16:47.362` | `client.log.2` | 442 | `ssl` | [GSpice       ][deal_udt_ssl_connect                  :6517] fd sesslssion(fd = 109, type = 4, typeEx = 0) udt ssl connect success |
| `26-05-01 17:16:47.362` | `client.log.2` | 444 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 1 for session fd = 108, type = 1, typeEx = 0 |
| `26-05-01 17:16:47.362` | `client.log.2` | 445 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 1, link info channel type 1 |
| `26-05-01 17:16:47.362` | `client.log.2` | 447 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 108, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 1, channel ID 0 -> virtual channel ID 1 |
| `26-05-01 17:16:47.363` | `client.log.2` | 453 | `spice-link` | [GSpice       ][spice_channel_send_link               :1990] main-1:0: display bandwidth: 0 KB/s, playback bandwidth: 0 KB/s |
| `26-05-01 17:16:47.363` | `client.log.2` | 454 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:16:47.363` | `client.log.2` | 455 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] main-1:0: Monitor assist type:1 |
| `26-05-01 17:16:47.363` | `client.log.2` | 456 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] main-1:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:16:47.363` | `client.log.2` | 458 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] main-1:0: common_caps[0]:800 |
| `26-05-01 17:16:47.363` | `client.log.2` | 459 | `spice-link` | [GSpice       ][spice_channel_send_link               :2079] main-1:0: caps[0]:23E900 |
| `26-05-01 17:16:47.363` | `client.log.2` | 460 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] main-1:0: spice_channel_send_link end!!! |
| `26-05-01 17:16:47.386` | `client.log.2` | 461 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] main-1:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:16:47.386` | `client.log.2` | 462 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] main-1:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:16:47.386` | `client.log.2` | 463 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] main-1:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:16:47.386` | `client.log.2` | 464 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] main-1:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:16:49.451` | `client.log.2` | 498 | `result` | [             ][qoe_log_report                        :1081] --->[i] \|0\|2\|2\|3\|932f****94c1\|\|<uuid>\|main-1:0 takes 2154ms (socket: 3ms, business: 2151ms) connect success\|<uuid>\|0\|0\|210 |
| `26-05-01 17:16:49.495` | `client.log.2` | 627 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] cursor-4:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59884 |
| `26-05-01 17:16:49.496` | `client.log.2` | 636 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:49.496` | `client.log.2` | 643 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] display-2:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59885 |
| `26-05-01 17:16:49.496` | `client.log.2` | 650 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:49.497` | `client.log.2` | 658 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] inputs-3:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59886 |
| `26-05-01 17:16:49.497` | `client.log.2` | 661 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:49.497` | `client.log.2` | 672 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] record-6:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59887 |
| `26-05-01 17:16:49.497` | `client.log.2` | 676 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:49.498` | `client.log.2` | 694 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] playback-5:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59888 |
| `26-05-01 17:16:49.498` | `client.log.2` | 701 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:49.499` | `client.log.2` | 715 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 2 for session fd = 115, type = 1, typeEx = 0 |
| `26-05-01 17:16:49.499` | `client.log.2` | 716 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 2, link info channel type 5 |
| `26-05-01 17:16:49.499` | `client.log.2` | 719 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 115, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 5, channel ID 0 -> virtual channel ID 2 |
| `26-05-01 17:16:49.499` | `client.log.2` | 722 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:16:49.499` | `client.log.2` | 723 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 3 for session fd = 113, type = 1, typeEx = 0 |
| `26-05-01 17:16:49.499` | `client.log.2` | 724 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] playback-5:0: Monitor assist type:1 |
| `26-05-01 17:16:49.499` | `client.log.2` | 725 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 3, link info channel type 6 |
| `26-05-01 17:16:49.499` | `client.log.2` | 726 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] playback-5:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:16:49.499` | `client.log.2` | 729 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] playback-5:0: common_caps[0]:800 |
| `26-05-01 17:16:49.499` | `client.log.2` | 730 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 113, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 6, channel ID 0 -> virtual channel ID 3 |
| `26-05-01 17:16:49.499` | `client.log.2` | 731 | `spice-link` | [GSpice       ][spice_channel_send_link               :2079] playback-5:0: caps[0]:E |
| `26-05-01 17:16:49.500` | `client.log.2` | 732 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] playback-5:0: spice_channel_send_link end!!! |
| `26-05-01 17:16:49.500` | `client.log.2` | 735 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] playback-5:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:16:49.500` | `client.log.2` | 736 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 4 for session fd = 111, type = 1, typeEx = 0 |
| `26-05-01 17:16:49.500` | `client.log.2` | 738 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 4, link info channel type 3 |
| `26-05-01 17:16:49.500` | `client.log.2` | 740 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 111, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 3, channel ID 0 -> virtual channel ID 4 |
| `26-05-01 17:16:49.500` | `client.log.2` | 743 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 5 for session fd = 100, type = 1, typeEx = 0 |
| `26-05-01 17:16:49.500` | `client.log.2` | 744 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 5, link info channel type 2 |
| `26-05-01 17:16:49.500` | `client.log.2` | 747 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 100, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 2, channel ID 0 -> virtual channel ID 5 |
| `26-05-01 17:16:49.500` | `client.log.2` | 753 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 6 for session fd = 95, type = 1, typeEx = 0 |
| `26-05-01 17:16:49.500` | `client.log.2` | 755 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 6, link info channel type 4 |
| `26-05-01 17:16:49.500` | `client.log.2` | 757 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 95, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 4, channel ID 0 -> virtual channel ID 6 |
| `26-05-01 17:16:49.501` | `client.log.2` | 780 | `ice` | [QTApplication][initRedirectParams                    :9464] port[5100] proxy_port[] s_proxy_port[60065] proxy_type[ice], device_redirect_dest_port[5100]. |
| `26-05-01 17:16:49.502` | `client.log.2` | 799 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:16:49.502` | `client.log.2` | 800 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] cursor-4:0: Monitor assist type:1 |
| `26-05-01 17:16:49.502` | `client.log.2` | 801 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] cursor-4:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:16:49.502` | `client.log.2` | 802 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] cursor-4:0: common_caps[0]:800 |
| `26-05-01 17:16:49.502` | `client.log.2` | 803 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] cursor-4:0: spice_channel_send_link end!!! |
| `26-05-01 17:16:49.502` | `client.log.2` | 804 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] cursor-4:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:16:49.502` | `client.log.2` | 805 | `spice-link` | [GSpice       ][spice_channel_send_link               :2000] display-2:0: available physical memory of terminal is 1100038144 MB. |
| `26-05-01 17:16:49.503` | `client.log.2` | 808 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:16:49.503` | `client.log.2` | 809 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] display-2:0: Monitor assist type:1 |
| `26-05-01 17:16:49.503` | `client.log.2` | 810 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] display-2:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:16:49.503` | `client.log.2` | 811 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] display-2:0: common_caps[0]:A00 |
| `26-05-01 17:16:49.503` | `client.log.2` | 812 | `spice-link` | [GSpice       ][spice_channel_send_link               :2079] display-2:0: caps[0]:92108EC |
| `26-05-01 17:16:49.503` | `client.log.2` | 813 | `spice-link` | [GSpice       ][spice_channel_send_link               :2079] display-2:0: caps[1]:9 |
| `26-05-01 17:16:49.503` | `client.log.2` | 814 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] display-2:0: spice_channel_send_link end!!! |
| `26-05-01 17:16:49.503` | `client.log.2` | 815 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] display-2:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:16:49.503` | `client.log.2` | 816 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:16:49.503` | `client.log.2` | 817 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] inputs-3:0: Monitor assist type:1 |
| `26-05-01 17:16:49.503` | `client.log.2` | 818 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] inputs-3:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:16:49.503` | `client.log.2` | 819 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] inputs-3:0: common_caps[0]:800 |
| `26-05-01 17:16:49.503` | `client.log.2` | 820 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] inputs-3:0: spice_channel_send_link end!!! |
| `26-05-01 17:16:49.503` | `client.log.2` | 821 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] inputs-3:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:16:49.503` | `client.log.2` | 822 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:16:49.503` | `client.log.2` | 823 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] record-6:0: Monitor assist type:1 |
| `26-05-01 17:16:49.503` | `client.log.2` | 824 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] record-6:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:16:49.503` | `client.log.2` | 825 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] record-6:0: common_caps[0]:800 |
| `26-05-01 17:16:49.503` | `client.log.2` | 826 | `spice-link` | [GSpice       ][spice_channel_send_link               :2079] record-6:0: caps[0]:7 |
| `26-05-01 17:16:49.503` | `client.log.2` | 827 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] record-6:0: spice_channel_send_link end!!! |
| `26-05-01 17:16:49.503` | `client.log.2` | 828 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] record-6:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:16:49.511` | `client.log.2` | 870 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] playback-5:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:16:49.511` | `client.log.2` | 871 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] playback-5:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:16:49.511` | `client.log.2` | 872 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] playback-5:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:16:49.513` | `client.log.2` | 874 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] cursor-4:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:16:49.513` | `client.log.2` | 875 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] cursor-4:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:16:49.513` | `client.log.2` | 876 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] cursor-4:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:16:49.516` | `client.log.2` | 878 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] display-2:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:16:49.516` | `client.log.2` | 879 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] display-2:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:16:49.516` | `client.log.2` | 880 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] display-2:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:16:49.517` | `client.log.2` | 882 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] inputs-3:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:16:49.517` | `client.log.2` | 883 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] inputs-3:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:16:49.517` | `client.log.2` | 884 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] inputs-3:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:16:49.517` | `client.log.2` | 886 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] record-6:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:16:49.517` | `client.log.2` | 887 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] record-6:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:16:49.517` | `client.log.2` | 888 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] record-6:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:16:49.522` | `client.log.2` | 891 | `result` | [             ][qoe_log_report                        :1081] --->[i] \|0\|2\|2\|3\|932f****94c1\|\|<uuid>\|playback-5:0 takes 31ms (socket: 7ms, business: 24ms) connect success\|<uuid>\|0\|0\|210 |
| `26-05-01 17:16:49.524` | `client.log.2` | 897 | `result` | [             ][qoe_log_report                        :1081] --->[i] \|0\|2\|2\|3\|932f****94c1\|\|<uuid>\|cursor-4:0 takes 41ms (socket: 12ms, business: 29ms) connect success\|<uuid>\|0\|0\|210 |
| `26-05-01 17:16:49.532` | `client.log.2` | 904 | `result` | [             ][qoe_log_report                        :1081] --->[i] \|0\|2\|2\|3\|932f****94c1\|\|<uuid>\|display-2:0 takes 45ms (socket: 9ms, business: 36ms) connect success\|<uuid>\|0\|0\|210 |
| `26-05-01 17:16:49.547` | `client.log.2` | 928 | `result` | [QTApplication][session_connect_success               : 265] session connect success |
| `26-05-01 17:16:49.550` | `client.log.2` | 987 | `ice` | [QTApplication][initRedirectParams                    :9464] port[5100] proxy_port[] s_proxy_port[60065] proxy_type[ice], device_redirect_dest_port[5100]. |
| `26-05-01 17:16:49.674` | `client.log.2` | 1561 | `result` | [             ][qoe_log_report                        :1081] --->[i] \|0\|2\|2\|3\|932f****94c1\|\|<uuid>\|inputs-3:0 takes 185ms (socket: 8ms, business: 177ms) connect success\|<uuid>\|0\|0\|210 |
| `26-05-01 17:16:49.679` | `client.log.2` | 1563 | `result` | [             ][qoe_log_report                        :1081] --->[i] \|0\|2\|2\|3\|932f****94c1\|\|<uuid>\|record-6:0 takes 188ms (socket: 6ms, business: 182ms) connect success\|<uuid>\|0\|0\|210 |
| `26-05-01 17:16:49.679` | `client.log.2` | 1564 | `result` | [             ][qoe_log_report                        :1081] --->[i] \|0\|2\|2\|100\|932f****94c1\|\|<uuid>\|connect success,start_time:2026-05-01 17:16:31,end_time:2026-05-01 17:16:49,connect_type:0,net_type:11,gate_way_ip:36.133.100.80,net_protocol:0,ip:192.168.5.14\|<uuid>\|0\|18125\|210 |
| `26-05-01 17:16:49.679` | `client.log.2` | 1566 | `result` | [GSpice       ][opentelemetry_qoe_export              : 693] data {"resourceSpans":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"terminal_spice"}},{"key":"telemetry.sdk.version","value":{"stringValue":"1.16.1"}},{"key":"telemetry.sdk.name","value":{"stringValue":"opentelemetry"}},{"key":"telemetry.sdk.language","value":{"stringValue":"cpp"}}]},"scopeSpans":[{"scope":{"name":"terminal_spice"},"spans":[{"status":{"code":1},"kind":3,"flags":1,"name":"spice connect","endTimeUnixNano":"1777****7000","spanId":"<redacted>","startTimeUnixNano":"1777****3000","traceId":"<redacted>","parentSpanId":"<redacted>","attributes":[{"key":"createtime","value":{"stringValue":"2026-05-01T17:16:47.000 +08:00"}},{"key":"trace_level","value":{"intValue":"1"}},{"key":"vmid","value":{"stringValue":"<uuid>"}},{"key":"userno","value":{"stringValue":"932f****94c1"}},{"key":"module_name","value":{"stringValue":"terminal_spice"}},{"key":"serviceId","value":{"intValue":"2"}},{"key":"uuid","value":{"stringValue":""}},{"key":"termid","value":{"stringValue":""}},{"key":"process_id","value":{"intValue":"2"}},{"key":"target_module","value":{"intValue":"210"}},{"key":"command_line","value":{"stringValue":" ./../MacOS/uSmartView_VDI_Client --guest-passwd <redacted> --guest-usr <redacted> -p 5100 --hv6 2409:8c70:3a50:24f7::2aa -k *** --pv6 5100 -f --vmid <redacted> --sambatype 0 --ostype 4 --usb-redirect-auto enable --proxy-sport 60065 --type ice --server-type hy --ms 1 --kbd-ct 20 --ds 30 --tnu 1 --dfst-small 300 --dfst-big 500 --ucc 0 --net-clip 3 --net-widthpeak 6000 --ra 0 --av1 0 --algo-mode 2 --vp9 0 --udt-ind-tmn 0 --qoe-name <redacted> --kbd-d 1 --kbd-dt 30 --kbd-ddmt 500 --kbd-ddr 30 --vid-stuck 1:1000:30:30 --voi-stuck 1:5:50:6 --pass-through <redacted> --connect_type 1 --net-type 1 --udt-multiex 1 -r enable -j enable --printer-redirect enable --play-lockscreen 0 --hub-ratio 1 --lockscreen-quit 0 --logoff-time 0 --limitScreen 0 --usb-redirect enable:0001****0000:DenyUSB=VID_0489&PID_E00D;VID_0BDA&PID_C8C2;VID_0489&PID_E046;VID_301A&PID_4601;VID_1C4F&PID_2502;VID_138A&PID_0008;VID_258A&PID_001E;VID_1C4F&PID_007F;VID_0489&PID_E032;VID_3547&PID_0407;VID_147E&PID_2016;VID_1C4F&PID_0050:AllowUSB=VID_03F0&PID_3E05;VID_067B&PID_23C3;VID_067B&PID_23A3;VID_067B&PID_2303;VID_04C5&PID_11F3;VID_04C5&PID_114F;VID_040A&PID_601C;VID_1A86&PID_7523;VID_03F0&PID_2B17;VID_1A86&PID_7522;VID_345F&PID_3020;VID_04B8&PID_011E;VID_1A86&PID_5523;VID_0403&PID_6014 -d enable -a enable --LVacc 0 --usb-disk all --usbredirecttype mdisk --link-integrat 1 --cdredirtype udisk -c enable -v enable --cf enable --vf enable -g all --sys-disk enable --sys-dir /boot;/root --cm 0,3000x3000,15 --clarity 3 --optimize 0000****1111 --stream x264 --accessToken <redacted> --qos 6\|5 --user-mode 0 --cpsid <redacted> --snd-stuck loss=10:time=0:mse=32 --redirect-mode 0 --quic-enable 2 --trace-level 2 --token-logon 0 --zmcep 0:0 --netchecktime 250 -t *** --logon_type 0 --qoeip 39.173.116.232 --st 1777626991554 --sn <redacted> --ad-ddq 3 --vmcip 10.21.2.232 --vmcport 8443 --https 1 --lang zh --enableIros2020 0 --httpsOnewayAuthentication 0 --ag-ip 36.133.100.80 --ag-port 8899 --internal 0 --server-type hy --authsvraddr (null) --otlp-trace-id <redacted> --otlp-parent-id <redacted> success"}},{"key":"log_type","value":{"intValue":"0"}},{"key":"subprocess_id","value":{"intValue":"3"}},{"key":"time","value":{"stringValue":"2026-05-01T17:16:49.000 +08:00"}}]}]}]}]} |
| `26-05-01 17:16:49.679` | `client.log.2` | 1567 | `result` | [GSpice       ][opentelemetry_qoe_export              : 693] data {"resourceSpans":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"terminal_spice"}},{"key":"telemetry.sdk.version","value":{"stringValue":"1.16.1"}},{"key":"telemetry.sdk.name","value":{"stringValue":"opentelemetry"}},{"key":"telemetry.sdk.language","value":{"stringValue":"cpp"}}]},"scopeSpans":[{"scope":{"name":"terminal_spice"},"spans":[{"status":{"code":1},"kind":3,"flags":1,"name":"spice connect","endTimeUnixNano":"1777****7000","spanId":"<redacted>","startTimeUnixNano":"1777****4000","traceId":"<redacted>","parentSpanId":"<redacted>","attributes":[{"key":"createtime","value":{"stringValue":"2026-05-01T17:16:49.000 +08:00"}},{"key":"trace_level","value":{"intValue":"1"}},{"key":"vmid","value":{"stringValue":"<uuid>"}},{"key":"userno","value":{"stringValue":"932f****94c1"}},{"key":"module_name","value":{"stringValue":"terminal_spice"}},{"key":"serviceId","value":{"intValue":"2"}},{"key":"uuid","value":{"stringValue":""}},{"key":"termid","value":{"stringValue":""}},{"key":"process_id","value":{"intValue":"2"}},{"key":"target_module","value":{"intValue":"210"}},{"key":"command_line","value":{"stringValue":" ./../MacOS/uSmartView_VDI_Client --guest-passwd <redacted> --guest-usr <redacted> -p 5100 --hv6 2409:8c70:3a50:24f7::2aa -k *** --pv6 5100 -f --vmid <redacted> --sambatype 0 --ostype 4 --usb-redirect-auto enable --proxy-sport 60065 --type ice --server-type hy --ms 1 --kbd-ct 20 --ds 30 --tnu 1 --dfst-small 300 --dfst-big 500 --ucc 0 --net-clip 3 --net-widthpeak 6000 --ra 0 --av1 0 --algo-mode 2 --vp9 0 --udt-ind-tmn 0 --qoe-name <redacted> --kbd-d 1 --kbd-dt 30 --kbd-ddmt 500 --kbd-ddr 30 --vid-stuck 1:1000:30:30 --voi-stuck 1:5:50:6 --pass-through <redacted> --connect_type 1 --net-type 1 --udt-multiex 1 -r enable -j enable --printer-redirect enable --play-lockscreen 0 --hub-ratio 1 --lockscreen-quit 0 --logoff-time 0 --limitScreen 0 --usb-redirect enable:0001****0000:DenyUSB=VID_0489&PID_E00D;VID_0BDA&PID_C8C2;VID_0489&PID_E046;VID_301A&PID_4601;VID_1C4F&PID_2502;VID_138A&PID_0008;VID_258A&PID_001E;VID_1C4F&PID_007F;VID_0489&PID_E032;VID_3547&PID_0407;VID_147E&PID_2016;VID_1C4F&PID_0050:AllowUSB=VID_03F0&PID_3E05;VID_067B&PID_23C3;VID_067B&PID_23A3;VID_067B&PID_2303;VID_04C5&PID_11F3;VID_04C5&PID_114F;VID_040A&PID_601C;VID_1A86&PID_7523;VID_03F0&PID_2B17;VID_1A86&PID_7522;VID_345F&PID_3020;VID_04B8&PID_011E;VID_1A86&PID_5523;VID_0403&PID_6014 -d enable -a enable --LVacc 0 --usb-disk all --usbredirecttype mdisk --link-integrat 1 --cdredirtype udisk -c enable -v enable --cf enable --vf enable -g all --sys-disk enable --sys-dir /boot;/root --cm 0,3000x3000,15 --clarity 3 --optimize 0000****1111 --stream x264 --accessToken <redacted> --qos 6\|5 --user-mode 0 --cpsid <redacted> --snd-stuck loss=10:time=0:mse=32 --redirect-mode 0 --quic-enable 2 --trace-level 2 --token-logon 0 --zmcep 0:0 --netchecktime 250 -t *** --logon_type 0 --qoeip 39.173.116.232 --st 1777626991554 --sn <redacted> --ad-ddq 3 --vmcip 10.21.2.232 --vmcport 8443 --https 1 --lang zh --enableIros2020 0 --httpsOnewayAuthentication 0 --ag-ip 36.133.100.80 --ag-port 8899 --internal 0 --server-type hy --authsvraddr (null) --otlp-trace-id <redacted> --otlp-parent-id <redacted> success"}},{"key":"log_type","value":{"intValue":"0"}},{"key":"subprocess_id","value":{"intValue":"100"}},{"key":"time","value":{"stringValue":"2026-05-01T17:16:49.000 +08:00"}}]}]}]}]} |
| `26-05-01 17:16:49.679` | `client.log.2` | 1568 | `spice` | [GSpice       ][spice_session_channel_connected       :6229] all channel 6/6 connect success |
| `26-05-01 17:16:50.302` | `client.log.2` | 1638 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9226] [PROXY] Creating proxy fd session, fd_type_ex=5 |
| `26-05-01 17:16:50.302` | `client.log.2` | 1639 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9236] [PROXY] Setting up outband proxy link (type=2) |
| `26-05-01 17:16:50.302` | `client.log.2` | 1640 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9250] [PROXY] Creating UDP proxy fd session |
| `26-05-01 17:16:50.302` | `client.log.2` | 1654 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9273] [PROXY] Assigning outband proxy socket |
| `26-05-01 17:16:50.302` | `client.log.2` | 1655 | `proxy` | [GSpice       ][deal_create_proxy_fd_session          :9277] [PROXY] Proxy fd session creation completed successfully |
| `26-05-01 17:16:50.302` | `client.log.2` | 1656 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:50.303` | `client.log.2` | 1662 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5704] [UDP] Successfully created UDT session for 36.133.100.80:8899 |
| `26-05-01 17:16:50.303` | `client.log.2` | 1664 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5736] client is support quic:0 (proxy_sock->link_type:2 proxy_sock->be_ssl:0 kcp->be_ssl:0 kcp->be_multi:0 g_enable_udt_stream:0 pThread->enable_quic:0, proxy_sock->use_quic:0) |
| `26-05-01 17:16:50.304` | `client.log.2` | 1681 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:50.323` | `client.log.2` | 1685 | `kcp` | [GSpice       ][deal_kcp_auth_cmd                     :6439] kcp(syn_id = <redacted>, conv = <redacted>)recv IKCP_CONV_AUTH_HEAD_ACK from:36.133.100.80:8899 |
| `26-05-01 17:16:50.344` | `client.log.2` | 1686 | `kcp` | [GSpice       ][deal_kcp_auth_cmd                     :6445] kcp(syn_id = <redacted>, conv = <redacted>) recv IKCP_CONV_AUTH_ACK from:36.133.100.80:8899 |
| `26-05-01 17:16:50.357` | `client.log.2` | 1687 | `kcp` | [GSpice       ][deal_kcp_sync_ack_cmd                 :6603] kcp(syn_id=<redacted>, conv=<redacted>) recv IKCP_CONV_SYNACK from:36.133.100.80:8899 |
| `26-05-01 17:16:50.357` | `client.log.2` | 1688 | `kcp` | [GSpice       ][deal_kcp_sync_ack_cmd                 :6604] kcp(syn_id=<redacted>, conv=<redacted>) be_quic=0 be_using_stream=0 be_ssl=0 |
| `26-05-01 17:16:50.357` | `client.log.2` | 1689 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 7 for session fd = 119, type = 1, typeEx = 0 |
| `26-05-01 17:16:50.357` | `client.log.2` | 1690 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4910] Configuring non-SPICE link type for virtual channel ID 7, link info channel type 12, using outband channel type |
| `26-05-01 17:16:50.357` | `client.log.2` | 1693 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 119, type = 1, typeEx = 0: destination 127.0.0.1:3246, channel type 0, channel ID 0 -> virtual channel ID 7 |
| `26-05-01 17:16:50.363` | `client.log.2` | 1694 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 8 for session fd = 123, type = 1, typeEx = 0 |
| `26-05-01 17:16:50.363` | `client.log.2` | 1695 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4910] Configuring non-SPICE link type for virtual channel ID 8, link info channel type 12, using outband channel type |
| `26-05-01 17:16:50.363` | `client.log.2` | 1697 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 123, type = 1, typeEx = 0: destination 127.0.0.1:3246, channel type 0, channel ID 0 -> virtual channel ID 8 |
| `26-05-01 17:16:50.583` | `client.log.2` | 1717 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:50.589` | `client.log.2` | 1719 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 9 for session fd = 120, type = 1, typeEx = 0 |
| `26-05-01 17:16:50.589` | `client.log.2` | 1720 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4910] Configuring non-SPICE link type for virtual channel ID 9, link info channel type 12, using outband channel type |
| `26-05-01 17:16:50.589` | `client.log.2` | 1722 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 120, type = 1, typeEx = 0: destination 127.0.0.1:3246, channel type 0, channel ID 0 -> virtual channel ID 9 |
| `26-05-01 17:16:51.689` | `client.log.2` | 1960 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] inputs-3:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59896 |
| `26-05-01 17:16:51.689` | `client.log.2` | 1964 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:51.690` | `client.log.2` | 1975 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] cursor-4:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59897 |
| `26-05-01 17:16:51.690` | `client.log.2` | 1978 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1981 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 10 for session fd = 111, type = 1, typeEx = 0 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1982 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 10, link info channel type 4 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1984 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 111, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 4, channel ID 0 -> virtual channel ID 10 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1986 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 11 for session fd = 95, type = 1, typeEx = 0 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1987 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 11, link info channel type 3 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1989 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 95, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 3, channel ID 0 -> virtual channel ID 11 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1990 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1991 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] cursor-4:0: Monitor assist type:1 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1992 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] cursor-4:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:16:51.696` | `client.log.2` | 1993 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] cursor-4:0: common_caps[0]:800 |
| `26-05-01 17:16:51.696` | `client.log.2` | 1994 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] cursor-4:0: spice_channel_send_link end!!! |
| `26-05-01 17:16:51.696` | `client.log.2` | 1995 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] cursor-4:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:16:51.697` | `client.log.2` | 1996 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:16:51.697` | `client.log.2` | 1997 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] inputs-3:0: Monitor assist type:1 |
| `26-05-01 17:16:51.697` | `client.log.2` | 1998 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] inputs-3:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:16:51.697` | `client.log.2` | 1999 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] inputs-3:0: common_caps[0]:800 |
| `26-05-01 17:16:51.697` | `client.log.2` | 2000 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] inputs-3:0: spice_channel_send_link end!!! |
| `26-05-01 17:16:51.697` | `client.log.2` | 2001 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] inputs-3:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:16:51.708` | `client.log.2` | 2002 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] cursor-4:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:16:51.708` | `client.log.2` | 2003 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] cursor-4:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:16:51.708` | `client.log.2` | 2004 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] cursor-4:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:16:51.710` | `client.log.2` | 2006 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] inputs-3:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:16:51.710` | `client.log.2` | 2007 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] inputs-3:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:16:51.710` | `client.log.2` | 2008 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] inputs-3:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:16:51.719` | `client.log.2` | 2011 | `result` | [GSpice       ][spice_processtrack_details_add        : 712] cursor-4:0 takes 30ms (socket: 1ms, business: 29ms) connect success |
| `26-05-01 17:16:51.720` | `client.log.2` | 2013 | `result` | [GSpice       ][spice_processtrack_details_add        : 712] inputs-3:0 takes 31ms (socket: 0ms, business: 31ms) connect success |
| `26-05-01 17:16:52.500` | `client.log.2` | 2063 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:16:52.505` | `client.log.2` | 2065 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 12 for session fd = 122, type = 1, typeEx = 0 |
| `26-05-01 17:16:52.505` | `client.log.2` | 2066 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4910] Configuring non-SPICE link type for virtual channel ID 12, link info channel type 12, using outband channel type |
| `26-05-01 17:16:52.506` | `client.log.2` | 2069 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 122, type = 1, typeEx = 0: destination 127.0.0.1:3246, channel type 0, channel ID 0 -> virtual channel ID 12 |
| `26-05-01 17:18:12.215` | `client.log.2` | 2534 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] inputs-3:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59925 |
| `26-05-01 17:18:12.215` | `client.log.2` | 2537 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:18:12.217` | `client.log.2` | 2557 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] cursor-4:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59926 |
| `26-05-01 17:18:12.217` | `client.log.2` | 2559 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2562 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 13 for session fd = 111, type = 1, typeEx = 0 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2563 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 13, link info channel type 4 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2565 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 111, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 4, channel ID 0 -> virtual channel ID 13 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2567 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 14 for session fd = 95, type = 1, typeEx = 0 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2568 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 14, link info channel type 3 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2570 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2571 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 95, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 3, channel ID 0 -> virtual channel ID 14 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2572 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] cursor-4:0: Monitor assist type:1 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2573 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] cursor-4:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:18:12.224` | `client.log.2` | 2574 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] cursor-4:0: common_caps[0]:800 |
| `26-05-01 17:18:12.224` | `client.log.2` | 2575 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] cursor-4:0: spice_channel_send_link end!!! |
| `26-05-01 17:18:12.224` | `client.log.2` | 2576 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] cursor-4:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:18:12.225` | `client.log.2` | 2577 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:18:12.225` | `client.log.2` | 2578 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] inputs-3:0: Monitor assist type:1 |
| `26-05-01 17:18:12.225` | `client.log.2` | 2579 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] inputs-3:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:18:12.225` | `client.log.2` | 2580 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] inputs-3:0: common_caps[0]:800 |
| `26-05-01 17:18:12.225` | `client.log.2` | 2581 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] inputs-3:0: spice_channel_send_link end!!! |
| `26-05-01 17:18:12.225` | `client.log.2` | 2582 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] inputs-3:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:18:12.239` | `client.log.2` | 2583 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] cursor-4:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:18:12.240` | `client.log.2` | 2584 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] cursor-4:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:18:12.240` | `client.log.2` | 2585 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] cursor-4:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:18:12.240` | `client.log.2` | 2587 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] inputs-3:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:18:12.241` | `client.log.2` | 2588 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] inputs-3:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:18:12.241` | `client.log.2` | 2589 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] inputs-3:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:18:12.254` | `client.log.2` | 2592 | `result` | [GSpice       ][spice_processtrack_details_add        : 712] cursor-4:0 takes 38ms (socket: 0ms, business: 38ms) connect success |
| `26-05-01 17:18:12.254` | `client.log.2` | 2594 | `result` | [GSpice       ][spice_processtrack_details_add        : 712] inputs-3:0 takes 40ms (socket: 1ms, business: 39ms) connect success |
| `26-05-01 17:18:18.842` | `client.log.2` | 2859 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] inputs-3:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59927 |
| `26-05-01 17:18:18.843` | `client.log.2` | 2861 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:18:18.849` | `client.log.2` | 2888 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] cursor-4:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59928 |
| `26-05-01 17:18:18.849` | `client.log.2` | 2891 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:18:18.855` | `client.log.2` | 2894 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 15 for session fd = 111, type = 1, typeEx = 0 |
| `26-05-01 17:18:18.855` | `client.log.2` | 2895 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 15, link info channel type 4 |
| `26-05-01 17:18:18.855` | `client.log.2` | 2897 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 111, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 4, channel ID 0 -> virtual channel ID 15 |
| `26-05-01 17:18:18.855` | `client.log.2` | 2898 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2900 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] cursor-4:0: Monitor assist type:1 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2901 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 16 for session fd = 95, type = 1, typeEx = 0 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2902 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] cursor-4:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:18:18.856` | `client.log.2` | 2903 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 16, link info channel type 3 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2904 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] cursor-4:0: common_caps[0]:800 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2906 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] cursor-4:0: spice_channel_send_link end!!! |
| `26-05-01 17:18:18.856` | `client.log.2` | 2907 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 95, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 3, channel ID 0 -> virtual channel ID 16 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2908 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] cursor-4:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:18:18.856` | `client.log.2` | 2909 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2910 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] inputs-3:0: Monitor assist type:1 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2911 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] inputs-3:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:18:18.856` | `client.log.2` | 2912 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] inputs-3:0: common_caps[0]:800 |
| `26-05-01 17:18:18.856` | `client.log.2` | 2913 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] inputs-3:0: spice_channel_send_link end!!! |
| `26-05-01 17:18:18.857` | `client.log.2` | 2914 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] inputs-3:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:18:18.869` | `client.log.2` | 2915 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] cursor-4:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:18:18.869` | `client.log.2` | 2916 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] cursor-4:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:18:18.869` | `client.log.2` | 2917 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] cursor-4:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:18:18.872` | `client.log.2` | 2919 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2188] inputs-3:0: spice_channel_recv_link_hdr end!!! |
| `26-05-01 17:18:18.872` | `client.log.2` | 2920 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2567] inputs-3:0: spice_channel_recv_link_msg start!!! |
| `26-05-01 17:18:18.872` | `client.log.2` | 2921 | `spice-link` | [GSpice       ][spice_channel_recv_link_msg           :2648] inputs-3:0: spice_channel_recv_link_msg end!!!! |
| `26-05-01 17:18:18.880` | `client.log.2` | 2924 | `result` | [GSpice       ][spice_processtrack_details_add        : 712] cursor-4:0 takes 32ms (socket: 0ms, business: 32ms) connect success |
| `26-05-01 17:18:18.883` | `client.log.2` | 2926 | `result` | [GSpice       ][spice_processtrack_details_add        : 712] inputs-3:0 takes 42ms (socket: 1ms, business: 41ms) connect success |
| `26-05-01 17:18:22.326` | `client.log.2` | 3198 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] inputs-3:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59931 |
| `26-05-01 17:18:22.327` | `client.log.2` | 3205 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:18:22.328` | `client.log.2` | 3223 | `local-spice` | [GSpice       ][spice_channel_print_connect_info      :3130] cursor-4:0: socket connect to 127.0.0.1:59882 success with 127.0.0.1:59932 |
| `26-05-01 17:18:22.329` | `client.log.2` | 3226 | `kcp` | [GSpice       ][init_local_rw_sock_pair_udp           :5659] [UDP] Initializing UDP socket pair with destination 36.133.100.80:8899 |
| `26-05-01 17:18:22.335` | `client.log.2` | 3236 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 17 for session fd = 111, type = 1, typeEx = 0 |
| `26-05-01 17:18:22.335` | `client.log.2` | 3237 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 17, link info channel type 4 |
| `26-05-01 17:18:22.335` | `client.log.2` | 3239 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 111, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 4, channel ID 0 -> virtual channel ID 17 |
| `26-05-01 17:18:22.336` | `client.log.2` | 3241 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4844] Allocated virtual channel ID 18 for session fd = 95, type = 1, typeEx = 0 |
| `26-05-01 17:18:22.336` | `client.log.2` | 3242 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4899] Configuring SPICE link type for virtual channel ID 18, link info channel type 3 |
| `26-05-01 17:18:22.336` | `client.log.2` | 3244 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| `26-05-01 17:18:22.336` | `client.log.2` | 3245 | `tunnel` | [GSpice       ][send_tunnel_add_link                  :4943] Successfully established tunnel link for session fd = 95, type = 1, typeEx = 0: destination [IPv6]:60065, channel type 3, channel ID 0 -> virtual channel ID 18 |
| `26-05-01 17:18:22.336` | `client.log.2` | 3246 | `spice-link` | [GSpice       ][spice_channel_send_link               :2034] cursor-4:0: Monitor assist type:1 |
| `26-05-01 17:18:22.336` | `client.log.2` | 3247 | `spice-link` | [GSpice       ][spice_channel_send_link               :2041] cursor-4:0: --->[s] send link msg required parameters[ae5****0] |
| `26-05-01 17:18:22.336` | `client.log.2` | 3248 | `spice-link` | [GSpice       ][spice_channel_send_link               :2072] cursor-4:0: common_caps[0]:800 |
| `26-05-01 17:18:22.336` | `client.log.2` | 3249 | `spice-link` | [GSpice       ][spice_channel_send_link               :2089] cursor-4:0: spice_channel_send_link end!!! |
| `26-05-01 17:18:22.336` | `client.log.2` | 3250 | `spice-link` | [GSpice       ][spice_channel_recv_link_hdr           :2164] cursor-4:0: spice_channel_recv_link_hdr start!!!! |
| `26-05-01 17:18:22.336` | `client.log.2` | 3251 | `spice-link` | [GSpice       ][spice_channel_send_link               :2019] b7c2****2b16 |
| ... | ... | ... | ... | 5649 events omitted by --limit |

## Offline Proxy Header Decode

```json
{
  "cmd": 26,
  "cmd_name": "ADD_LINK",
  "link_id": 1,
  "data_len": 154
}
```
