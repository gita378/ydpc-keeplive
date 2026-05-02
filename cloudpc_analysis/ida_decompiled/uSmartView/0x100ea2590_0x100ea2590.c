// 0x100ea2590 @ 0x100ea2590
__int64 __fastcall sub_100EA2590(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  unsigned int v6; // edx
  __int64 thread_proxy_fd_session; // [rsp+30h] [rbp-30h]

  if ( (_DWORD)a1 == 3 && a4 ) /*0x100ea25ba*/
  {
    if ( (unsigned int)spice_util_get_debug(a1, a2, a3, a4, a5, a6) && spice_gtk_log_level < 2 ) /*0x100ea25dd*/
      g_log( /*0x100ea264f*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] kcp(syn_id = 0x%x, conv = 0x%x) recv IKCP_CONV_FIN cmd from:%s:%d",
        (unsigned int)"deal_kcp_fin_ack_cmd",
        6679,
        *(_DWORD *)(a2 + 12416),
        *(_DWORD *)(a2 + 16),
        a2 + 12340,
        *(unsigned __int16 *)(a2 + 12404));
    if ( *(_BYTE *)(a2 + 12409) ) /*0x100ea265d*/
    {
      v6 = 5; /*0x100ea2681*/
      if ( *(_WORD *)(a4 + 396) == 1 ) /*0x100ea2686*/
        v6 = 6; /*0x100ea2686*/
      thread_proxy_fd_session = get_thread_proxy_fd_session(*(_QWORD *)(a4 + 232), v6); /*0x100ea269f*/
      set_fd_session_flag(thread_proxy_fd_session, 16, 6684); /*0x100ea26b1*/
    }
    ikcp_deal_fin(a2, a3); /*0x100ea26be*/
  }
  else if ( (_DWORD)a1 == 4 ) /*0x100ea26d0*/
  {
    if ( (unsigned int)spice_util_get_debug(a1, a2, a3, a4, a5, a6) && spice_gtk_log_level < 2 ) /*0x100ea26f3*/
      g_log( /*0x100ea2765*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] kcp(syn_id = 0x%x, conv = 0x%x) recv IKCP_CONV_FINACK cmd from:%s:%d",
        (unsigned int)"deal_kcp_fin_ack_cmd",
        6688,
        *(_DWORD *)(a2 + 12416),
        *(_DWORD *)(a2 + 16),
        a2 + 12340,
        *(unsigned __int16 *)(a2 + 12404));
    ikcp_deal_fin_ack(a2, a3); /*0x100ea2777*/
  }
  return 0; /*0x100ea2784*/
}
