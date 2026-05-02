// 0x100ea1e00 @ 0x100ea1e00
__int64 __fastcall sub_100EA1E00(
        __int64 a1,
        int a2,
        __int64 a3,
        unsigned __int16 a4,
        __int64 a5,
        __int64 a6,
        unsigned __int16 a7)
{
  __int64 v7; // rdi
  __int64 type; // rsi
  __int64 v9; // rdx
  __int64 v10; // r8
  __int64 v11; // r9
  unsigned __int16 v12; // ax
  __int64 v13; // r8
  __int64 v14; // r9
  __int64 v15; // rdi
  __int64 v16; // rdx
  __int64 v17; // r8
  __int64 v18; // r9
  __int64 v19; // rcx
  __int64 v21; // [rsp+18h] [rbp-68h]
  __int64 v22; // [rsp+30h] [rbp-50h]
  __int64 v23; // [rsp+38h] [rbp-48h]
  int v24; // [rsp+44h] [rbp-3Ch]
  unsigned int v25; // [rsp+44h] [rbp-3Ch]

  if ( !a5 ) /*0x100ea1e31*/
  {
    g_return_if_fail_warning("GSpice", "deal_kcp_auth_cmd", "kcp != NULL"); /*0x100ea1e51*/
    return 6; /*0x100ea1e5c*/
  }
  if ( !*(_QWORD *)(a5 + 304) ) /*0x100ea1e6f*/
  {
    g_return_if_fail_warning("GSpice", "deal_kcp_auth_cmd", "kcp->user_data != NULL"); /*0x100ea1e97*/
    return 6; /*0x100ea1ea2*/
  }
  v23 = *(_QWORD *)(a5 + 304); /*0x100ea1eb7*/
  if ( !a1 ) /*0x100ea1ec3*/
  {
    g_return_if_fail_warning("GSpice", "deal_kcp_auth_cmd", "NULL != in_sock"); /*0x100ea1ee3*/
    return 6; /*0x100ea1eee*/
  }
  if ( !*(_QWORD *)(a1 + 264) ) /*0x100ea1f05*/
  {
    g_return_if_fail_warning("GSpice", "deal_kcp_auth_cmd", "NULL != in_sock->session"); /*0x100ea1f2c*/
    return 6; /*0x100ea1f37*/
  }
  v7 = *(_QWORD *)(a1 + 264); /*0x100ea1f55*/
  type = spice_session_get_type(); /*0x100ea1f59*/
  v22 = g_type_instance_get_private(v7, type); /*0x100ea1f61*/
  if ( !v22 ) /*0x100ea1f6d*/
  {
    g_return_if_fail_warning("GSpice", "deal_kcp_auth_cmd", "NULL != s"); /*0x100ea1f8d*/
    return 6; /*0x100ea1f98*/
  }
  *(_DWORD *)(v22 + 6068) = 1; /*0x100ea1fa6*/
  if ( a2 == 7 ) /*0x100ea1fb8*/
  {
    if ( (unsigned int)spice_util_get_debug(v7, type, v9, 7, v10, v11) && spice_gtk_log_level < 2 ) /*0x100ea1fdb*/
      g_log( /*0x100ea203f*/
        (unsigned int)"GSpice",
        64,
        (unsigned int)"[%-38s:%4d] kcp(syn_id = 0x%x, conv = 0x%x)recv IKCP_CONV_AUTH_HEAD_ACK from:%s:%d",
        (unsigned int)"deal_kcp_auth_cmd",
        6439,
        *(_DWORD *)(a5 + 12416),
        *(_DWORD *)(a5 + 16),
        a3,
        a4);
    v12 = ikcp_set_auth_head_res(a5, a6, a7); /*0x100ea2057*/
    v24 = v12; /*0x100ea205f*/
    if ( v12 != 200 ) /*0x100ea2069*/
    {
      if ( (unsigned int)spice_util_get_debug(a5, a6, 200, v12, v13, v14) ) /*0x100ea2074*/
        g_log( /*0x100ea20a8*/
          (unsigned int)"GSpice",
          8,
          (unsigned int)"[%-38s:%4d] ikcp_set_auth_head_res, code[%d].",
          (unsigned int)"deal_kcp_auth_cmd",
          6441,
          v24);
      return 6; /*0x100ea20b8*/
    }
    return 0; /*0x100ea2205*/
  }
  if ( a2 != 9 ) /*0x100ea20ca*/
    return 0; /*0x100ea20ca*/
  if ( (unsigned int)spice_util_get_debug(v7, type, v9, 7, v10, v11) && spice_gtk_log_level < 2 ) /*0x100ea20ed*/
  {
    HIDWORD(v21) = a4; /*0x100ea2120*/
    LODWORD(v21) = *(_DWORD *)(a5 + 16); /*0x100ea212d*/
    g_log( /*0x100ea2151*/
      (unsigned int)"GSpice",
      64,
      (unsigned int)"[%-38s:%4d] kcp(syn_id = 0x%x, conv = 0x%x) recv IKCP_CONV_AUTH_ACK from:%s:%d",
      (unsigned int)"deal_kcp_auth_cmd",
      6445,
      *(_DWORD *)(a5 + 12416),
      v21,
      a3,
      a4,
      v21);
  }
  v15 = a5; /*0x100ea215b*/
  v25 = (unsigned __int16)ikcp_set_auth_data_res(a5, a6, a7); /*0x100ea2171*/
  if ( v25 == 200 ) /*0x100ea217c*/
  {
    *(_BYTE *)(v23 + 133) = 1; /*0x100ea21f9*/
    return 0; /*0x100ea21f9*/
  }
  v19 = 6; /*0x100ea2186*/
  if ( *(_DWORD *)(a1 + 36) == 6 ) /*0x100ea218e*/
  {
    *(_DWORD *)(a1 + 88) = 1; /*0x100ea2198*/
    v15 = v25; /*0x100ea219f*/
    spice_session_handle_cag_err(v25); /*0x100ea21a2*/
  }
  if ( (unsigned int)spice_util_get_debug(v15, a6, v16, v19, v17, v18) ) /*0x100ea21ac*/
    g_log( /*0x100ea21e0*/
      (unsigned int)"GSpice",
      8,
      (unsigned int)"[%-38s:%4d] ikcp_set_auth_data_res, code[%d].",
      (unsigned int)"deal_kcp_auth_cmd",
      6452,
      v25);
  return 6; /*0x100ea220f*/
}
