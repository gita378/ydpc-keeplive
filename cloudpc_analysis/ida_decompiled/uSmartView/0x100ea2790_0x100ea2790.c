// 0x100ea2790 @ 0x100ea2790
__int64 __fastcall sub_100EA2790(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  __int64 type; // rax
  __int64 v7; // rdi
  __int64 v8; // rdx
  __int64 v9; // r8
  __int64 v10; // r9
  __int64 v12; // [rsp+0h] [rbp-70h]
  __int64 v13; // [rsp+8h] [rbp-68h]
  __int64 v14; // [rsp+10h] [rbp-60h]
  __int64 v15; // [rsp+28h] [rbp-48h]
  __int64 v16; // [rsp+38h] [rbp-38h]
  unsigned int proxy_type_by_link_type; // [rsp+44h] [rbp-2Ch]
  __int64 thread_proxy_fd_session; // [rsp+48h] [rbp-28h]

  if ( (_DWORD)a1 == 5 )
  {
    if ( (unsigned int)spice_util_get_debug(a1, a2, a3, a4, a5, a6) && spice_gtk_log_level < 2 ) /*0x100ea27e1*/
      g_log( /*0x100ea2853*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] kcp(syn_id = 0x%x, conv = 0x%x) recv IKCP_CONV_RST cmd from:%s:%d",
        (unsigned int)"deal_kcp_rst_cmd",
        6700,
        *(_DWORD *)(a2 + 12416),
        *(_DWORD *)(a2 + 16),
        a2 + 12340,
        *(unsigned __int16 *)(a2 + 12404));
    if ( *(_BYTE *)(a2 + 12409) && a4 )
    {
      v15 = *(_QWORD *)(a4 + 264); /*0x100ea2887*/
      type = spice_session_get_type(); /*0x100ea288b*/
      v16 = g_type_instance_get_private(v15, type); /*0x100ea289c*/
      proxy_type_by_link_type = get_proxy_type_by_link_type(*(_QWORD *)(a4 + 264), *(unsigned __int16 *)(a4 + 396)); /*0x100ea28bb*/
      v7 = *(_QWORD *)(a4 + 232); /*0x100ea28c2*/
      thread_proxy_fd_session = get_thread_proxy_fd_session(v7, proxy_type_by_link_type); /*0x100ea28d1*/
      if ( thread_proxy_fd_session )
      {
        if ( *(_DWORD *)(thread_proxy_fd_session + 36) == 6 )
        {
          *(_DWORD *)(v16 + 5096) = 1; /*0x100ea28f6*/
          *(_DWORD *)(v16 + 6584) = 1; /*0x100ea2904*/
          if ( (unsigned int)spice_util_get_debug(v7, proxy_type_by_link_type, v8, 6, v9, v10) )
          {
            if ( spice_gtk_log_level < 2 )
            {
              LODWORD(v12) = *(_DWORD *)(a2 + 16); /*0x100ea2989*/
              LODWORD(v13) = *(_DWORD *)(v16 + 5096); /*0x100ea2991*/
              LODWORD(v14) = *(_DWORD *)(v16 + 6584); /*0x100ea299a*/
              g_log(
                (unsigned int)"GSpice",
                64,
                (unsigned int)"[%-38s:%4d] kcp(syn_id = 0x%x, conv = 0x%x) enable_link_unify_proxy_reconnect: %d recv_lin"
                              "k_unify_kcp_rst_msg: %d",
                (unsigned int)"deal_kcp_rst_cmd",
                6708,
                *(_DWORD *)(a2 + 12416),
                v12,
                v13,
                v14);
            }
          }
        }
      }
      set_fd_session_flag(thread_proxy_fd_session, 16, 6710); /*0x100ea29be*/
    }
    ikcp_deal_rst(a2); /*0x100ea29c7*/
  }
  return 0; /*0x100ea29cf*/
}
