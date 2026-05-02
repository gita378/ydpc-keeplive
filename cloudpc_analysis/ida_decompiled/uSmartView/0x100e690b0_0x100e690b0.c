// 0x100e690b0 @ 0x100e690b0
__int64 __fastcall ice_deal_cag_init_tcp_read(__int64 a1, __int64 a2)
{
  __int64 LastError; // rdi
  __int16 v3; // ax
  __int64 v4; // rdx
  __int64 v5; // r8
  __int64 v6; // r9
  __int64 v7; // rcx
  int v9; // [rsp+0h] [rbp-30h]
  int v10; // [rsp+8h] [rbp-28h]
  int v11; // [rsp+14h] [rbp-1Ch]
  int v12; // [rsp+18h] [rbp-18h]
  int v13; // [rsp+1Ch] [rbp-14h]

  v13 = 0; /*0x100e690bc*/
  while ( 1 ) /*0x100e690c9*/
  {
    if ( ++v13 >= 10 ) /*0x100e690cf*/
      return 0; /*0x100e690cf*/
    LastError = a1; /*0x100e690d5*/
    v3 = ice_udp_tcp_sock_func_read(a1); /*0x100e690d9*/
    v7 = (unsigned int)v3; /*0x100e690de*/
    v12 = v3; /*0x100e690e1*/
    if ( v3 <= 0 ) /*0x100e690e8*/
      break; /*0x100e690e8*/
    *(_QWORD *)(a1 + 72) = ice_get_ms(); /*0x100e690f9*/
    *(_DWORD *)(a1 + 60) += v12; /*0x100e69107*/
    if ( *(_DWORD *)(a1 + 60) >= *(_DWORD *)(a1 + 64) ) /*0x100e69118*/
      ice_deal_cag_reply(a1); /*0x100e69122*/
  }
  if ( v3 ) /*0x100e69131*/
  {
    LastError = (unsigned int)tcpGetLastError(); /*0x100e6913e*/
    if ( !(unsigned int)sub_100E68790(LastError) ) /*0x100e69148*/
      return 0; /*0x100e691ee*/
  }
  if ( (unsigned int)spice_util_get_debug(LastError, a2, v4, v7, v5, v6) && spice_gtk_log_level < 2 ) /*0x100e6916b*/
  {
    v11 = *(_DWORD *)(a1 + 16); /*0x100e6917e*/
    v9 = v12; /*0x100e691b2*/
    v10 = tcpGetLastError(); /*0x100e691b6*/
    g_log( /*0x100e691bc*/
      (unsigned int)"GSpice",
      64,
      (unsigned int)"[%-38s:%4d] sock[%d] read buf fail,read-len:%d errno:%d",
      (unsigned int)"ice_deal_cag_init_tcp_read",
      956,
      v11,
      v9,
      v10);
  }
  ice_set_socket_flag_ex(a1, 16, 957); /*0x100e691d4*/
  return 1; /*0x100e691f8*/
}
