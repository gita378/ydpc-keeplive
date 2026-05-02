// 0x100e9ef20 @ 0x100e9ef20
__int64 __fastcall sub_100E9EF20(_QWORD *a1, char a2)
{
  __int64 type; // rax
  __int64 v3; // rax
  __int64 v4; // rax
  __int64 v5; // rsi
  __int64 v6; // rdi
  __int64 v7; // rdx
  __int64 v8; // r8
  __int64 v9; // r9
  char *v11; // [rsp+48h] [rbp-B8h]
  unsigned __int16 v12; // [rsp+58h] [rbp-A8h]
  __int64 v13; // [rsp+60h] [rbp-A0h]
  unsigned __int16 *v14; // [rsp+70h] [rbp-90h]
  __int64 v15; // [rsp+88h] [rbp-78h]
  int v16; // [rsp+90h] [rbp-70h]
  int v17; // [rsp+94h] [rbp-6Ch]
  int connect_processtrack_id; // [rsp+98h] [rbp-68h]
  unsigned __int16 v19; // [rsp+9Ch] [rbp-64h]
  char *v20; // [rsp+A0h] [rbp-60h]
  __int64 v21; // [rsp+A8h] [rbp-58h]
  int v22; // [rsp+B4h] [rbp-4Ch]
  __int64 v23; // [rsp+B8h] [rbp-48h]
  _BOOL4 v24; // [rsp+C4h] [rbp-3Ch]
  __int64 v25; // [rsp+C8h] [rbp-38h]
  in_addr_t v29[3]; // [rsp+ECh] [rbp-14h] BYREF

  v25 = a1[38]; /*0x100e9ef4b*/
  if ( v25 )
  {
    v24 = 0; /*0x100e9ef89*/
    v13 = *(_QWORD *)(v25 + 264); /*0x100e9ef9b*/
    type = spice_session_get_type(); /*0x100e9efa2*/
    v23 = g_type_instance_get_private(v13, type); /*0x100e9efb6*/
    v22 = 0; /*0x100e9efba*/
    v20 = *(char **)v23; /*0x100e9efd0*/
    if ( *(_DWORD *)(v23 + 3048) == 1 ) /*0x100e9efe3*/
      v12 = ZXStrtol(*(_QWORD *)(v23 + 2592), 10); /*0x100e9effe*/
    else
      v12 = ZXStrtol(*(_QWORD *)(v23 + 2584), 10); /*0x100e9f01f*/
    v19 = v12; /*0x100e9f02d*/
    connect_processtrack_id = spice_processtrack_get_connect_processtrack_id(*(_QWORD *)(v25 + 264)); /*0x100e9f042*/
    v17 = 11; /*0x100e9f045*/
    if ( !strcmp(*(const char **)(v23 + 2656), "ice") ) /*0x100e9f064*/
    {
      v19 = ZXStrtol(*(_QWORD *)(v23 + 8), 10); /*0x100e9f089*/
      v17 = 139; /*0x100e9f094*/
    }
    if ( *(_WORD *)(v25 + 396) == 2 ) /*0x100e9f0a9*/
    {
      if ( !strcmp(*(const char **)(v23 + 2656), "ice") ) /*0x100e9f0c9*/
        v11 = *(char **)v23; /*0x100e9f0e3*/
      else
        v11 = (char *)(v23 + 4940); /*0x100e9f0f9*/
      v20 = v11; /*0x100e9f107*/
      v19 = ZXStrtol(*(_QWORD *)(v23 + 5872), 10); /*0x100e9f120*/
      v17 = 140; /*0x100e9f132*/
    }
    else if ( *(_WORD *)(v25 + 396) == 1 ) /*0x100e9f14c*/
    {
      v24 = *(_DWORD *)(v23 + 3716) == 0; /*0x100e9f169*/
    }
    if ( (unsigned int)sub_100E9F6F0(a1, v20) )
    {
      if ( (unsigned int)g_strcmp0(*(_QWORD *)(v23 + 2648), "2") ) /*0x100e9f1a4*/
        v21 = *(_QWORD *)(v23 + 3160); /*0x100e9f1d2*/
      else
        v21 = *(_QWORD *)(v23 + 3560); /*0x100e9f1be*/
      if ( v21 ) /*0x100e9f1db*/
      {
        v22 = ZXStrlen(v21, 1024) + 1; /*0x100e9f1f5*/
        if ( v22 % 16 ) /*0x100e9f201*/
          v22 = 16 * (v22 / 16 + 1); /*0x100e9f21d*/
      }
      v16 = v22 + 176; /*0x100e9f22f*/
      if ( v24 ) /*0x100e9f236*/
        v16 = v22 + 304; /*0x100e9f246*/
      v15 = spice_malloc0(v16); /*0x100e9f252*/
      if ( v15 )
      {
        v3 = ZXStrlen("ZTEC", 4); /*0x100e9f2af*/
        ZXMemcpy(v15, 4, "ZTEC", v3); /*0x100e9f2ca*/
        *(_WORD *)(v15 + 4) = v16 - (v22 + 132); /*0x100e9f2e5*/
        *(_DWORD *)(v15 + 6) = 102; /*0x100e9f302*/
        *(_DWORD *)(v15 + 10) = ZXRand(); /*0x100e9f31c*/
        *(_DWORD *)(v15 + 14) = v22 + 126; /*0x100e9f331*/
        *(_DWORD *)(v15 + 34) |= v17 << 16; /*0x100e9f344*/
        *(_DWORD *)(v15 + 34) |= (v17 & 0x7F) << 24; /*0x100e9f35a*/
        spice_processtrack_get_serial_num(*(_QWORD *)(v23 + 8LL * connect_processtrack_id + 2848), v15 + 18, 16); /*0x100e9f380*/
        if ( v24 ) /*0x100e9f394*/
        {
          *(_DWORD *)(v15 + 34) |= 4u; /*0x100e9f3ae*/
          ZXSnprintf(v15 + 114, 64, "%s", g_otlp_parent_id); /*0x100e9f3e0*/
          ZXSnprintf(v15 + 50, 64, "%s", g_otlp_trace_id); /*0x100e9f40b*/
          v14 = (unsigned __int16 *)(v15 + 178); /*0x100e9f422*/
        }
        else
        {
          v14 = (unsigned __int16 *)(v15 + 50); /*0x100e9f43e*/
        }
        if ( *(_QWORD *)(v23 + 3272) ) /*0x100e9f449*/
          ZXSnprintf(v14 + 30, 32, "%s", *(const char **)(v23 + 3272)); /*0x100e9f480*/
        if ( v22 > 0 ) /*0x100e9f489*/
        {
          v4 = ZXStrlen(v21, v22 - 1); /*0x100e9f4c9*/
          ZXMemcpy(v14 + 63, v22, v21, v4); /*0x100e9f4e6*/
        }
        *v14 = v19; /*0x100e9f4f5*/
        v14[62] = v22; /*0x100e9f502*/
        if ( (unsigned int)check_ip_addr_family(v20) == 2 ) /*0x100e9f516*/
        {
          v5 = (__int64)v20; /*0x100e9f51c*/
          v6 = 30; /*0x100e9f52d*/
          inet_pton(30, v20, v14 + 2); /*0x100e9f535*/
          v14[46] = 1; /*0x100e9f541*/
        }
        else
        {
          v29[0] = inet_addr(v20); /*0x100e9f555*/
          v6 = (__int64)(v14 + 2); /*0x100e9f571*/
          v5 = 16; /*0x100e9f574*/
          ZXMemcpy(v14 + 2, 16, v29, 4); /*0x100e9f57e*/
        }
        if ( *(_QWORD *)(v23 + 2576) ) /*0x100e9f587*/
        {
          v6 = (__int64)(v14 + 10); /*0x100e9f5ad*/
          v5 = 40; /*0x100e9f5b0*/
          ZXSnprintf(v14 + 10, 40, "%s", *(const char **)(v23 + 2576)); /*0x100e9f5be*/
        }
        a1[3408] = deal_udt_cag_auth; /*0x100e9f5ce*/
        a1[3409] = deal_udt_cag_auth_res; /*0x100e9f5e0*/
        if ( (unsigned int)spice_util_get_debug(v6, v5, v7, deal_udt_cag_auth_res, v8, v9) && spice_gtk_log_level < 2 )
          g_log(
            (unsigned int)"GSpice",
            64,
            (unsigned int)"[%-38s:%4d] set kcp cag connect dst: %s:%u",
            (unsigned int)"deal_udt_using_cag_uac",
            5437,
            (_DWORD)v20,
            *v14);
        ikcp_set_auth_data( /*0x100e9f69d*/
          (__int64)a1,
          v15,
          *(_WORD *)(v15 + 4) + 6,
          *(_DWORD *)(v15 + 14),
          *(_DWORD *)(v15 + 10),
          a2,
          1,
          1);
        g_free(v15); /*0x100e9f6a6*/
        return 0; /*0x100e9f6ab*/
      }
      else
      {
        g_return_if_fail_warning("GSpice", "deal_udt_using_cag_uac", "pBuffer != NULL"); /*0x100e9f27b*/
        return 1; /*0x100e9f280*/
      }
    }
    else
    {
      return 1; /*0x100e9f187*/
    }
  }
  else
  {
    g_return_if_fail_warning("GSpice", "deal_udt_using_cag_uac", "udp_sock != NULL"); /*0x100e9ef74*/
    return 1; /*0x100e9ef79*/
  }
}
