// 0x100e6c950 @ 0x100e6c950
__int64 __fastcall sub_100E6C950(__int64 a1, char a2)
{
  __int64 v2; // rax
  int *v3; // rdi
  __int64 v4; // rsi
  __int64 v5; // rdx
  __int64 v6; // r8
  __int64 v7; // r9
  _WORD *v9; // [rsp+40h] [rbp-70h]
  int v10; // [rsp+4Ch] [rbp-64h]
  _WORD *v11; // [rsp+50h] [rbp-60h]
  int v12; // [rsp+5Ch] [rbp-54h]
  __int64 v13; // [rsp+60h] [rbp-50h]
  int *v14; // [rsp+68h] [rbp-48h]
  __int64 v15; // [rsp+70h] [rbp-40h]
  __int64 v16; // [rsp+78h] [rbp-38h]
  int v17; // [rsp+80h] [rbp-30h]
  int v18; // [rsp+80h] [rbp-30h]
  _DWORD v22[3]; // [rsp+9Ch] [rbp-14h] BYREF

  v13 = 0; /*0x100e6c98f*/
  v12 = 11; /*0x100e6c997*/
  if ( g_is_ice ) /*0x100e6c9a5*/
    v12 = 139; /*0x100e6c9b3*/
  ZXMemset(&g_cag_param, 232, 0, 232); /*0x100e6c9cd*/
  if ( (unsigned int)check_ip_addr_family(&g_destip) == 2 ) /*0x100e6c9e8*/
  {
    inet_pton(30, &g_destip, &unk_103358420); /*0x100e6ca0a*/
    byte_103358461 |= 1u; /*0x100e6ca19*/
  }
  else
  {
    v22[0] = inet_addr(&g_destip); /*0x100e6ca3e*/
    ZXMemcpy(&unk_103358420, 16, v22, 4); /*0x100e6ca59*/
  }
  word_103358430 = g_destport; /*0x100e6ca65*/
  word_1033584E0 = ZXStrlen(g_passwd, 1024); /*0x100e6ca8b*/
  qword_1033584E8 = (__int64)g_passwd; /*0x100e6ca99*/
  ZXMemcpy(&unk_103358410, 16, &g_conn_serial_num, 16); /*0x100e6cab2*/
  ZXSnprintf(&unk_103358432, 40, "%s", (const char *)qoe_vmid); /*0x100e6caee*/
  ZXSnprintf(&unk_1033584A0, 64, "%s", g_username); /*0x100e6cb19*/
  if ( g_auth_type ) /*0x100e6cb26*/
  {
    word_10335840C = 2; /*0x100e6cd2d*/
    v10 = ZXStrlen(g_passwd, 1024); /*0x100e6cd47*/
    if ( v10 % 16 ) /*0x100e6cd53*/
      v10 = 16 * (v10 / 16 + 1); /*0x100e6cd6f*/
    if ( g_has_connected ) /*0x100e6cd79*/
      v18 = v10 + 176; /*0x100e6cd9b*/
    else
      v18 = v10 + 304; /*0x100e6cd89*/
    v16 = spice_malloc0(v18); /*0x100e6cda7*/
    if ( !v16 ) /*0x100e6cdb0*/
      goto LABEL_11; /*0x100e6cdb0*/
    v15 = v16; /*0x100e6cde9*/
    *(_WORD *)(v16 + 4) = v18 - 132 - v10; /*0x100e6ce08*/
    v14 = (int *)(v16 + 6); /*0x100e6ce17*/
    *(_DWORD *)(v16 + 6) = 102; /*0x100e6ce1f*/
    *(_DWORD *)(v16 + 14) = v10 + 126; /*0x100e6ce34*/
    if ( g_has_connected ) /*0x100e6ce46*/
    {
      v9 = (_WORD *)(v16 + 50); /*0x100e6ce5c*/
    }
    else
    {
      v13 = v16 + 6; /*0x100e6ce6f*/
      v9 = (_WORD *)(v16 + 178); /*0x100e6ce83*/
    }
    ZXSnprintf(v9 + 30, 32, "%s", g_username); /*0x100e6cea9*/
    ZXSnprintf(v9 + 10, 40, "%s", (const char *)qoe_vmid); /*0x100e6ced1*/
    if ( (unsigned int)check_ip_addr_family(&g_destip) == 2 ) /*0x100e6cee9*/
    {
      inet_pton(30, &g_destip, v9 + 2); /*0x100e6cf08*/
      v9[46] = 1; /*0x100e6cf11*/
    }
    else
    {
      ZXMemcpy(v9 + 2, 16, v22, 4); /*0x100e6cf41*/
    }
    *v9 = g_destport; /*0x100e6cf51*/
    v9[62] = v10; /*0x100e6cf5b*/
  }
  else
  {
    word_10335840C = 1; /*0x100e6cb2c*/
    if ( g_has_connected ) /*0x100e6cb3c*/
      v17 = 270; /*0x100e6cb42*/
    else
      v17 = 398; /*0x100e6cb4e*/
    v16 = spice_malloc0(v17); /*0x100e6cb5e*/
    if ( !v16 ) /*0x100e6cb67*/
    {
LABEL_11:
      g_return_if_fail_warning("GSpice", "ice_deal_using_ng", "pBuffer != NULL"); /*0x100e6cb6d*/
      return (unsigned int)-1; /*0x100e6cb92*/
    }
    v15 = v16; /*0x100e6cba0*/
    *(_WORD *)(v16 + 4) = v17 - 226; /*0x100e6cbb8*/
    v14 = (int *)(v16 + 6); /*0x100e6cbc7*/
    *(_DWORD *)(v16 + 6) = 101; /*0x100e6cbcf*/
    *(_DWORD *)(v16 + 14) = 220; /*0x100e6cbd9*/
    if ( g_has_connected ) /*0x100e6cbef*/
    {
      v11 = (_WORD *)(v16 + 50); /*0x100e6cc05*/
    }
    else
    {
      v13 = v16 + 6; /*0x100e6cc18*/
      v11 = (_WORD *)(v16 + 178); /*0x100e6cc2c*/
    }
    ZXSnprintf(v11 + 30, 64, "%s", g_username); /*0x100e6cc52*/
    ZXSnprintf(v11 + 62, 64, "%s", g_passwd); /*0x100e6cc7a*/
    ZXSnprintf(v11 + 10, 40, "%s", (const char *)qoe_vmid); /*0x100e6cca2*/
    if ( (unsigned int)check_ip_addr_family(&g_destip) == 2 ) /*0x100e6ccba*/
    {
      inet_pton(30, &g_destip, v11 + 2); /*0x100e6ccd9*/
      v11[94] = 1; /*0x100e6cce2*/
    }
    else
    {
      ZXMemcpy(v11 + 2, 16, v22, 4); /*0x100e6cd15*/
    }
    *v11 = g_destport; /*0x100e6cd25*/
  }
  v2 = ZXStrlen("ZTEC", 4); /*0x100e6cf76*/
  ZXMemcpy(v15, 4, "ZTEC", v2); /*0x100e6cf91*/
  v14[1] = ZXRand(); /*0x100e6cfa7*/
  v14[7] |= v12 << 16; /*0x100e6cfb7*/
  v14[7] |= (v12 & 0x7F) << 24; /*0x100e6cfca*/
  v3 = v14 + 3; /*0x100e6cfd8*/
  v4 = 16; /*0x100e6cfe0*/
  ZXMemcpy(v14 + 3, 16, &g_conn_serial_num, 16); /*0x100e6cfea*/
  if ( v13 ) /*0x100e6cff4*/
  {
    v14[7] |= 4u; /*0x100e6d00b*/
    ZXSnprintf(v13 + 108, 64, "%s", g_otlp_parent_id); /*0x100e6d029*/
    v3 = (int *)(v13 + 44); /*0x100e6d040*/
    v4 = 64; /*0x100e6d043*/
    ZXSnprintf(v13 + 44, 64, "%s", g_otlp_trace_id); /*0x100e6d051*/
  }
  *(_QWORD *)(a1 + 27264) = ice_deal_udt_auth; /*0x100e6d061*/
  *(_QWORD *)(a1 + 27272) = ice_deal_udt_auth_res; /*0x100e6d073*/
  if ( (unsigned int)spice_util_get_debug(v3, v4, v5, ice_deal_udt_auth_res, v6, v7) && spice_gtk_log_level < 2 ) /*0x100e6d092*/
    g_log( /*0x100e6d0cb*/
      (unsigned int)"GSpice",
      64,
      (unsigned int)"[%-38s:%4d] ice_deal_using_ng send auth data, destip[%s], destport[%d]!!",
      (unsigned int)"ice_deal_using_ng",
      3571,
      (unsigned int)&g_destip,
      (unsigned __int16)g_destport);
  ikcp_set_auth_data(a1, v16, *(_WORD *)(v15 + 4) + 6, v14[2], v14[1], a2, 1, 1); /*0x100e6d119*/
  g_free(v16); /*0x100e6d122*/
  return 0; /*0x100e6d15b*/
}
