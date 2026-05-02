// 0x100e8b2c0 @ 0x100e8b2c0
__int64 __fastcall send_tunnel_delete_link(__int64 a1)
{
  const char *v1; // rdi
  __int64 type; // rsi
  __int64 v3; // r8
  __int64 v4; // r9
  __int64 v5; // rdx
  __int64 v6; // rcx
  __int64 v7; // r8
  __int64 v8; // r9
  __int64 fd_session_log_print_info; // rax
  unsigned __int64 v10; // rsi
  __int64 v11; // rdi
  __int64 v12; // rdx
  __int64 v13; // rcx
  __int64 v14; // r8
  __int64 v15; // r9
  int v16; // eax
  __int64 v18; // [rsp+0h] [rbp-150h]
  __int64 v19; // [rsp+8h] [rbp-148h]
  int v20; // [rsp+44h] [rbp-10Ch]
  bool v21; // [rsp+5Fh] [rbp-F1h]
  __int64 thread_proxy_fd_session; // [rsp+70h] [rbp-E0h]
  unsigned int proxy_type_by_link_type; // [rsp+7Ch] [rbp-D4h]
  int v24; // [rsp+8Ch] [rbp-C4h]
  __int64 v26; // [rsp+A0h] [rbp-B0h]
  _WORD v27[4]; // [rsp+B8h] [rbp-98h] BYREF
  _BYTE __b[136]; // [rsp+C0h] [rbp-90h] BYREF

  if ( !a1 ) /*0x100e8b2e8*/
  {
    g_return_if_fail_warning("GSpice", "send_tunnel_delete_link", "in_sock != NULL"); /*0x100e8b308*/
    return __stack_chk_guard; /*0x100e8b30d*/
  }
  if ( *(_DWORD *)(a1 + 32) == 1 )
  {
    sub_100E8B820(a1); /*0x100e8b334*/
    memset(__b, 0, 0x80u); /*0x100e8b352*/
    memset(v27, 0, sizeof(v27)); /*0x100e8b36c*/
    v24 = delete_session_channel_manage_by_fd(*(_QWORD *)(a1 + 264), *(unsigned int *)(a1 + 24)); /*0x100e8b38e*/
    if ( v24 > 0 )
    {
      LOBYTE(v27[0]) = 42; /*0x100e8b3bb*/
      HIBYTE(v27[0]) = v24; /*0x100e8b3cb*/
      v27[1] = 4; /*0x100e8b3d5*/
      v1 = *(const char **)(a1 + 264); /*0x100e8b40d*/
      type = spice_session_get_type(); /*0x100e8b414*/
      v26 = g_type_instance_get_private(v1, type); /*0x100e8b41e*/
      v21 = 0; /*0x100e8b433*/
      if ( *(_DWORD *)(v26 + 5940) ) /*0x100e8b42c*/
      {
        v21 = 0; /*0x100e8b44c*/
        if ( *(int *)(a1 + 52) >= 0 ) /*0x100e8b452*/
          v21 = *(_DWORD *)(a1 + 32) == 1; /*0x100e8b466*/
      }
      if ( (unsigned int)spice_util_get_debug(v1, type, 0, v21, v3, v4) && spice_gtk_log_level < 1 )
      {
        v1 = "GSpice"; /*0x100e8b4ec*/
        type = 128; /*0x100e8b4fb*/
        g_log(
          (unsigned int)"GSpice",
          128,
          (unsigned int)"[%-38s:%4d] fd:%d Port channel check(result:%d) - enable_flag: %d, channel_id: %d, fd_type: %d, "
                        "be_port_channel: %d, line: %d",
          (unsigned int)"check_is_port_channel_related_sock",
          4698,
          *(_DWORD *)(a1 + 24),
          v21,
          *(_DWORD *)(v26 + 5940),
          *(_DWORD *)(a1 + 52),
          *(_DWORD *)(a1 + 32),
          *(_DWORD *)(a1 + 56),
          5097);
      }
      if ( v21 ) /*0x100e8b472*/
      {
        if ( *(_DWORD *)(a1 + 64) ) /*0x100e8b589*/
        {
          if ( (unsigned int)spice_util_get_debug(v1, type, v5, v6, v7, v8) && spice_gtk_log_level < 3 ) /*0x100e8b5b0*/
          {
            v20 = *(_DWORD *)(a1 + 52); /*0x100e8b5d4*/
            fd_session_log_print_info = get_fd_session_log_print_info(a1, __b, 128); /*0x100e8b5db*/
            LODWORD(v19) = v24; /*0x100e8b621*/
            g_log( /*0x100e8b628*/
              (unsigned int)"GSpice",
              16,
              (unsigned int)"[%-38s:%4d] port channel(%d) closed, suspend send fd session(%s) tunnel close (link id = %d) cmd message",
              (unsigned int)"send_tunnel_delete_link",
              5099,
              v20,
              fd_session_log_print_info,
              v19);
          }
          return __stack_chk_guard; /*0x100e8b628*/
        }
        v10 = (unsigned __int64)v27; /*0x100e8b637*/
        v11 = a1; /*0x100e8b63e*/
        sub_100E8BA10(a1, v27, 8); /*0x100e8b64a*/
      }
      else
      {
        proxy_type_by_link_type = get_proxy_type_by_link_type(*(_QWORD *)(a1 + 264), *(unsigned __int16 *)(a1 + 396)); /*0x100e8b675*/
        thread_proxy_fd_session = get_thread_proxy_fd_session(*(_QWORD *)(a1 + 232), proxy_type_by_link_type); /*0x100e8b698*/
        if ( !thread_proxy_fd_session || (*(_DWORD *)(thread_proxy_fd_session + 40) & 0x10) != 0 ) /*0x100e8b6bc*/
          return __stack_chk_guard; /*0x100e8b6bc*/
        v10 = (unsigned __int64)v27; /*0x100e8b6c7*/
        v11 = thread_proxy_fd_session; /*0x100e8b6ce*/
        sub_100E8BF30(thread_proxy_fd_session, v27, 8); /*0x100e8b6da*/
        v13 = thread_proxy_fd_session; /*0x100e8b6df*/
        if ( *(_QWORD *)(thread_proxy_fd_session + 176) /*0x100e8b71b*/
          && !*(_BYTE *)(*(_QWORD *)(thread_proxy_fd_session + 176) + 27245LL)
          && *(_QWORD *)(a1 + 184) )
        {
          v11 = *(_QWORD *)(thread_proxy_fd_session + 176); /*0x100e8b730*/
          v10 = (unsigned __int8)**(_DWORD **)(a1 + 184); /*0x100e8b747*/
          ikcp_do_stream_destroy(v11, v10); /*0x100e8b74a*/
          v12 = a1; /*0x100e8b74f*/
          *(_QWORD *)(a1 + 184) = 0; /*0x100e8b756*/
        }
      }
      if ( (unsigned int)spice_util_get_debug(v11, v10, v12, v13, v14, v15) && spice_gtk_log_level < 2 ) /*0x100e8b78d*/
      {
        v16 = get_fd_session_log_print_info(a1, __b, 128); /*0x100e8b7a6*/
        LODWORD(v18) = v24; /*0x100e8b7e4*/
        g_log( /*0x100e8b7ea*/
          (unsigned int)"GSpice",
          64,
          (unsigned int)"[%-38s:%4d] fd session(%s) send tunnel close (link id = %d) cmd message",
          (unsigned int)"send_tunnel_delete_link",
          5121,
          v16,
          v18);
      }
    }
  }
  return __stack_chk_guard; /*0x100e8b80b*/
}
