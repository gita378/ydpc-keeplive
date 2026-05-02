// 0x100e9a620 @ 0x100e9a620
__int64 __fastcall sub_100E9A620(__int64 a1, __int64 a2)
{
  __int64 type; // rax
  __int64 v3; // r8
  __int64 v4; // r9
  __int64 v5; // rcx
  __int64 v6; // rdx
  int fd_session_log_print_info; // eax
  int v9; // [rsp+20h] [rbp-C0h]
  int v10; // [rsp+24h] [rbp-BCh]
  __int64 v11; // [rsp+28h] [rbp-B8h]
  __int64 v12; // [rsp+30h] [rbp-B0h]
  unsigned __int8 v13; // [rsp+3Fh] [rbp-A1h]
  _BYTE __b[136]; // [rsp+50h] [rbp-90h] BYREF

  if ( a1 ) /*0x100e9a64f*/
  {
    if ( a2 ) /*0x100e9a68b*/
    {
      v13 = *(_BYTE *)(a1 + 410); /*0x100e9a6c7*/
      if ( v13 < 7u ) /*0x100e9a6d7*/
      {
        v11 = *(_QWORD *)(a1 + 264); /*0x100e9a714*/
        type = spice_session_get_type(); /*0x100e9a71b*/
        v12 = g_type_instance_get_private(v11, type); /*0x100e9a731*/
        memset(__b, 0, 0x80u); /*0x100e9a747*/
        if ( *(_DWORD *)(*(_QWORD *)(a1 + 232) + 8LL * v13 + 8336) ) /*0x100e9a763*/
        {
          if ( v13 == 1 ) /*0x100e9a77f*/
          {
            if ( *(_DWORD *)(v12 + 5128) >= 0xFFFFu ) /*0x100e9a796*/
              LOWORD(v10) = -1; /*0x100e9a7b9*/
            else
              v10 = *(_DWORD *)(v12 + 5128); /*0x100e9a7a9*/
            v5 = a2; /*0x100e9a7ca*/
            *(_WORD *)(a2 + 81) = v10; /*0x100e9a7d1*/
          }
          else
          {
            if ( *(_DWORD *)(*(_QWORD *)(a1 + 232) + 8LL * v13 + 8336) >= 0xFFFFu ) /*0x100e9a7fc*/
              LOWORD(v9) = -1; /*0x100e9a830*/
            else
              v9 = *(_DWORD *)(*(_QWORD *)(a1 + 232) + 8LL * v13 + 8336); /*0x100e9a820*/
            v5 = a2; /*0x100e9a841*/
            *(_WORD *)(a2 + 79) = v9; /*0x100e9a848*/
          }
          LOBYTE(v5) = *(_BYTE *)(a1 + 410); /*0x100e9a853*/
          *(_BYTE *)(a2 + 3) = v5; /*0x100e9a860*/
          v6 = *(unsigned __int8 *)(a2 + 3) | 0x80u; /*0x100e9a86e*/
          *(_BYTE *)(a2 + 3) |= 0x80u; /*0x100e9a874*/
          if ( (unsigned int)spice_util_get_debug(__b, 0, v6, v5, v3, v4) && spice_gtk_log_level < 2 ) /*0x100e9a88f*/
          {
            fd_session_log_print_info = get_fd_session_log_print_info(a1, __b, 128); /*0x100e9a8a8*/
            g_log( /*0x100e9a913*/
              (unsigned int)"GSpice",
              64,
              (unsigned int)"[%-38s:%4d] [BW CTRL] fd session(%s) need downward bandwidth control, downward bandwidth = %"
                            "uKB/s, total downward bandwidth = %uKB/s",
              (unsigned int)"deal_bw_ctrl_sock_link_message",
              4516,
              fd_session_log_print_info,
              *(unsigned __int16 *)(a2 + 79),
              *(unsigned __int16 *)(a2 + 81));
          }
        }
      }
      else
      {
        g_return_if_fail_warning( /*0x100e9a6f7*/
          "GSpice",
          "deal_bw_ctrl_sock_link_message",
          "down_bw_ctrl_link_type < BW_CTRL_LINK_TYPE_END");
      }
    }
    else
    {
      g_return_if_fail_warning("GSpice", "deal_bw_ctrl_sock_link_message", "link_info_ex != NULL"); /*0x100e9a6ab*/
    }
  }
  else
  {
    g_return_if_fail_warning("GSpice", "deal_bw_ctrl_sock_link_message", "in_sock != NULL"); /*0x100e9a66f*/
  }
  return __stack_chk_guard; /*0x100e9a939*/
}
