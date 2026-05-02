// 0x100e8ab60 @ 0x100e8ab60
__int64 __fastcall sub_100E8AB60(__int64 a1, int a2, unsigned int a3)
{
  __int64 v3; // rdi
  __int64 v4; // rdx
  __int64 v5; // rcx
  __int64 v6; // r8
  __int64 v7; // r9
  int fd_session_log_print_info; // eax
  __int64 sock_by_port_channel_id; // [rsp+18h] [rbp-A8h]
  _BYTE __b[136]; // [rsp+30h] [rbp-90h] BYREF

  if ( a1 ) /*0x100e8ab94*/
  {
    memset(__b, 0, 0x80u); /*0x100e8abd4*/
    if ( *(_WORD *)(a1 + 396) == 1 ) /*0x100e8abee*/
    {
      if ( a2 == 2 ) /*0x100e8ac10*/
      {
        *(_BYTE *)(a1 + 409) = 2; /*0x100e8ac1d*/
        *(_DWORD *)(a1 + 392) = 5; /*0x100e8ac2b*/
        *(_BYTE *)(a1 + 410) = *(_BYTE *)(a1 + 409); /*0x100e8ac49*/
      }
      else if ( a2 != 10 || (unsigned int)is_port_channel_multiplex_enabled(*(_QWORD *)(a1 + 264)) ) /*0x100e8ac73*/
      {
        *(_BYTE *)(a1 + 409) = 1; /*0x100e8ad8b*/
        *(_BYTE *)(a1 + 410) = *(_BYTE *)(a1 + 409); /*0x100e8ada6*/
      }
      else
      {
        v3 = *(_QWORD *)(a1 + 232); /*0x100e8ac88*/
        sock_by_port_channel_id = get_sock_by_port_channel_id(v3, a3); /*0x100e8ac9a*/
        if ( sock_by_port_channel_id ) /*0x100e8aca9*/
        {
          LOBYTE(v5) = *(_BYTE *)(sock_by_port_channel_id + 409); /*0x100e8acb6*/
          *(_BYTE *)(a1 + 410) = v5; /*0x100e8acc3*/
        }
        else
        {
          *(_BYTE *)(a1 + 410) = 1; /*0x100e8acd5*/
        }
        *(_BYTE *)(a1 + 408) = 0; /*0x100e8ace3*/
        if ( (unsigned int)spice_util_get_debug(v3, a3, v4, v5, v6, v7) && spice_gtk_log_level < 2 ) /*0x100e8ad02*/
        {
          fd_session_log_print_info = get_fd_session_log_print_info(a1, __b, 128); /*0x100e8ad1b*/
          g_log( /*0x100e8ad75*/
            (unsigned int)"GSpice",
            64,
            (unsigned int)"[%-38s:%4d] [BW CTRL] set port channel fd session(%s) down bw ctrl type to [%s]",
            (unsigned int)"set_sock_bw_ctrl_type",
            4673,
            fd_session_log_print_info,
            bw_ctrl_type_str[*(unsigned __int8 *)(a1 + 410)]);
        }
      }
    }
    else
    {
      reset_sock_bw_ctrl_link_type_by_bw_config(a1); /*0x100e8abfb*/
    }
  }
  else
  {
    g_return_if_fail_warning("GSpice", "set_sock_bw_ctrl_type", "in_sock != NULL"); /*0x100e8abb4*/
  }
  return __stack_chk_guard; /*0x100e8adc8*/
}
