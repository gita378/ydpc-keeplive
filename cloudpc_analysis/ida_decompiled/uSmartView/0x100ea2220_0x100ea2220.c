// 0x100ea2220 @ 0x100ea2220
__int64 __fastcall sub_100EA2220(__int64 a1, int a2, __int64 a3, __int64 a4, __int16 a5, __int64 a6)
{
  __int64 v6; // rdx
  __int64 v7; // rcx
  __int64 v8; // r8
  __int64 v9; // r9
  const char *v10; // rdi
  __int64 v11; // rsi
  __int64 v12; // rdx
  __int64 v13; // rcx
  __int64 v14; // r8
  __int64 v15; // r9
  __int64 v16; // rdx
  __int64 v17; // rcx
  __int64 v18; // r8
  __int64 v19; // r9
  __int64 v20; // rdx
  __int64 v21; // rcx
  __int64 v22; // r8
  __int64 v23; // r9
  __int64 v25; // [rsp+0h] [rbp-80h]
  __int64 v26; // [rsp+8h] [rbp-78h]
  __int64 v27; // [rsp+10h] [rbp-70h]
  char v28; // [rsp+4Fh] [rbp-31h]

  if ( a2 == 1 ) /*0x100ea224b*/
  {
    ikcp_deal_link_sync(a3, a4); /*0x100ea2259*/
    if ( (unsigned int)spice_util_get_debug(a3, a4, v6, v7, v8, v9) && spice_gtk_log_level < 2 ) /*0x100ea2276*/
      g_log( /*0x100ea22e8*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] kcp(syn_id = 0x%x, conv = 0x%x) recv IKCP_CONV_SYN from:%s:%d",
        (unsigned int)"deal_kcp_sync_ack_cmd",
        6596,
        *(_DWORD *)(a3 + 12416),
        *(_DWORD *)(a3 + 16),
        a3 + 12340,
        *(unsigned __int16 *)(a3 + 12404));
    if ( a5 && *(_BYTE *)(a3 + 12407) ) /*0x100ea2303*/
      udt_init_ssl_link(*(_QWORD *)(a6 + 120), a6, 0); /*0x100ea2321*/
  }
  else if ( a2 == 2 ) /*0x100ea2333*/
  {
    v28 = *(_BYTE *)(a3 + 12409); /*0x100ea2343*/
    v10 = (const char *)a3; /*0x100ea2346*/
    v11 = a4; /*0x100ea234a*/
    ikcp_deal_svr_sync_ack(a3, a4); /*0x100ea234e*/
    if ( (unsigned int)spice_util_get_debug(a3, a4, v12, v13, v14, v15) && spice_gtk_log_level < 2 ) /*0x100ea236b*/
    {
      v10 = "GSpice"; /*0x100ea2398*/
      v11 = 64; /*0x100ea23a8*/
      g_log( /*0x100ea23dd*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] kcp(syn_id=0x%x, conv=0x%x) recv IKCP_CONV_SYNACK from:%s:%d",
        (unsigned int)"deal_kcp_sync_ack_cmd",
        6603,
        *(_DWORD *)(a3 + 12416),
        *(_DWORD *)(a3 + 16),
        a3 + 12340,
        *(unsigned __int16 *)(a3 + 12404));
    }
    if ( (unsigned int)spice_util_get_debug(v10, v11, v16, v17, v18, v19) && spice_gtk_log_level < 2 ) /*0x100ea2404*/
    {
      v10 = "GSpice"; /*0x100ea2447*/
      v11 = 64; /*0x100ea2453*/
      LODWORD(v25) = *(_DWORD *)(a3 + 16); /*0x100ea247a*/
      LODWORD(v26) = *(unsigned __int8 *)(a3 + 27244); /*0x100ea2482*/
      LODWORD(v27) = *(unsigned __int8 *)(a3 + 25232); /*0x100ea248b*/
      g_log( /*0x100ea249b*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] kcp(syn_id=0x%x, conv=0x%x) be_quic=%u be_using_stream=%u be_ssl=%u",
        (unsigned int)"deal_kcp_sync_ack_cmd",
        6604,
        *(_DWORD *)(a3 + 12416),
        v25,
        v26,
        v27,
        *(unsigned __int8 *)(a3 + 12407));
    }
    if ( !v28 && !*(_BYTE *)(a3 + 27245) ) /*0x100ea24b3*/
    {
      if ( *(_BYTE *)(a3 + 12407) ) /*0x100ea24c4*/
      {
        if ( (unsigned int)spice_util_get_debug(v10, v11, v20, v21, v22, v23) && spice_gtk_log_level < 2 ) /*0x100ea250d*/
        {
          LODWORD(v25) = *(_DWORD *)(a3 + 16); /*0x100ea254f*/
          g_log( /*0x100ea2555*/
            (unsigned int)"GSpice",
            64,
            (unsigned int)"[%-38s:%4d] kcp(syn_id = 0x%x, conv = 0x%x) has not ssl connected, will try to connect...",
            (unsigned int)"deal_kcp_sync_ack_cmd",
            6609,
            *(_DWORD *)(a3 + 12416),
            v25);
        }
        udt_init_ssl_link(*(_QWORD *)(a6 + 120), a6, 0); /*0x100ea256d*/
      }
      else
      {
        set_fd_session_flag(*(_QWORD *)(a6 + 200), 4, 6607); /*0x100ea24e6*/
      }
    }
  }
  return 0; /*0x100ea2584*/
}
