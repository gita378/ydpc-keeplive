// 0x100e9e490 @ 0x100e9e490
__int64 __fastcall sub_100E9E490(_QWORD *a1, unsigned int a2)
{
  __int64 type; // rax
  __int64 v3; // rax
  __int64 v4; // rsi
  __int64 v5; // rdi
  __int64 v6; // rdx
  __int64 v7; // r8
  __int64 v8; // r9
  char *v10; // [rsp+28h] [rbp-A8h]
  unsigned __int16 v11; // [rsp+38h] [rbp-98h]
  __int64 v12; // [rsp+40h] [rbp-90h]
  unsigned __int16 *v13; // [rsp+50h] [rbp-80h]
  __int64 v14; // [rsp+68h] [rbp-68h]
  int v15; // [rsp+74h] [rbp-5Ch]
  int connect_processtrack_id; // [rsp+78h] [rbp-58h]
  unsigned __int16 v17; // [rsp+7Ch] [rbp-54h]
  char *v18; // [rsp+80h] [rbp-50h]
  _BOOL4 v19; // [rsp+88h] [rbp-48h]
  int v20; // [rsp+8Ch] [rbp-44h]
  __int64 v21; // [rsp+90h] [rbp-40h]
  __int64 v22; // [rsp+98h] [rbp-38h]
  char v23; // [rsp+A4h] [rbp-2Ch]
  in_addr_t v26[3]; // [rsp+BCh] [rbp-14h] BYREF

  v23 = a2; /*0x100e9e4ad*/
  v22 = a1[38]; /*0x100e9e4bb*/
  if ( v22 )
  {
    v12 = *(_QWORD *)(v22 + 264); /*0x100e9e504*/
    type = spice_session_get_type(); /*0x100e9e50b*/
    v21 = g_type_instance_get_private(v12, type); /*0x100e9e51f*/
    v20 = 11; /*0x100e9e523*/
    v19 = 0; /*0x100e9e52a*/
    v18 = *(char **)v21; /*0x100e9e538*/
    if ( *(_DWORD *)(v21 + 3048) == 1 ) /*0x100e9e54b*/
      v11 = ZXStrtol(*(_QWORD *)(v21 + 2592), 10); /*0x100e9e566*/
    else
      v11 = ZXStrtol(*(_QWORD *)(v21 + 2584), 10); /*0x100e9e587*/
    v17 = v11; /*0x100e9e595*/
    connect_processtrack_id = spice_processtrack_get_connect_processtrack_id(*(_QWORD *)(v22 + 264)); /*0x100e9e5a8*/
    if ( (unsigned int)g_strcmp0(*(_QWORD *)(v21 + 2648), "1") && (unsigned int)g_strcmp0(*(_QWORD *)(v21 + 2648), "2") )
    {
      if ( !strcmp(*(const char **)(v21 + 2656), "ice") ) /*0x100e9e61c*/
      {
        v17 = ZXStrtol(*(_QWORD *)(v21 + 8), 10); /*0x100e9e641*/
        v20 = 139; /*0x100e9e64c*/
      }
      if ( *(_WORD *)(v22 + 396) == 2 ) /*0x100e9e661*/
      {
        if ( (unsigned int)g_strcmp0(*(_QWORD *)(v21 + 2656), "ice") ) /*0x100e9e679*/
          v10 = (char *)(v21 + 4940); /*0x100e9e6a5*/
        else
          v10 = *(char **)v21; /*0x100e9e68f*/
        v18 = v10; /*0x100e9e6b3*/
        v17 = ZXStrtol(*(_QWORD *)(v21 + 5872), 10); /*0x100e9e6cc*/
        v20 = 140; /*0x100e9e6de*/
      }
      else if ( *(_WORD *)(v22 + 396) == 1 ) /*0x100e9e6f8*/
      {
        v19 = *(_DWORD *)(v21 + 3716) == 0; /*0x100e9e715*/
      }
      if ( (unsigned int)sub_100E9F6F0(a1, v18) )
      {
        v15 = 270; /*0x100e9e73e*/
        if ( v19 ) /*0x100e9e749*/
          v15 = 398; /*0x100e9e74f*/
        v14 = spice_malloc0(v15); /*0x100e9e75f*/
        if ( v14 )
        {
          v3 = ZXStrlen("ZTEC", 4); /*0x100e9e7bc*/
          ZXMemcpy(v14, 4, "ZTEC", v3); /*0x100e9e7d7*/
          *(_WORD *)(v14 + 4) = v15 - 226; /*0x100e9e7f2*/
          *(_DWORD *)(v14 + 6) = 101; /*0x100e9e809*/
          *(_DWORD *)(v14 + 10) = ZXRand(); /*0x100e9e820*/
          *(_DWORD *)(v14 + 14) = 220; /*0x100e9e827*/
          *(_DWORD *)(v14 + 34) |= v20 << 16; /*0x100e9e83b*/
          *(_DWORD *)(v14 + 34) |= (v20 & 0x7F) << 24; /*0x100e9e84e*/
          spice_processtrack_get_serial_num(*(_QWORD *)(v21 + 8LL * connect_processtrack_id + 2848), v14 + 18, 16); /*0x100e9e874*/
          if ( v19 ) /*0x100e9e885*/
          {
            *(_DWORD *)(v14 + 34) |= 4u; /*0x100e9e89c*/
            ZXSnprintf(v14 + 114, 64, "%s", g_otlp_parent_id); /*0x100e9e8ce*/
            ZXSnprintf(v14 + 50, 64, "%s", g_otlp_trace_id); /*0x100e9e8f9*/
            v13 = (unsigned __int16 *)(v14 + 178); /*0x100e9e910*/
          }
          else
          {
            v13 = (unsigned __int16 *)(v14 + 50); /*0x100e9e929*/
          }
          if ( *(_QWORD *)(v21 + 3272) ) /*0x100e9e931*/
            ZXSnprintf(v13 + 30, 64, "%s", *(const char **)(v21 + 3272)); /*0x100e9e965*/
          if ( *(_QWORD *)(v21 + 3280) ) /*0x100e9e96e*/
            ZXSnprintf(v13 + 62, 64, "%s", *(const char **)(v21 + 3280)); /*0x100e9e9a2*/
          if ( (unsigned int)check_ip_addr_family(v18) == 2 ) /*0x100e9e9b7*/
          {
            v4 = (__int64)v18; /*0x100e9e9bd*/
            v5 = 30; /*0x100e9e9cb*/
            inet_pton(30, v18, v13 + 2); /*0x100e9e9d3*/
            v13[94] = 1; /*0x100e9e9dc*/
          }
          else
          {
            v26[0] = inet_addr(v18); /*0x100e9e9f3*/
            v5 = (__int64)(v13 + 2); /*0x100e9ea0c*/
            v4 = 16; /*0x100e9ea0f*/
            ZXMemcpy(v13 + 2, 16, v26, 4); /*0x100e9ea19*/
          }
          *v13 = v17; /*0x100e9ea25*/
          if ( *(_QWORD *)(v21 + 2576) ) /*0x100e9ea2c*/
          {
            v5 = (__int64)(v13 + 10); /*0x100e9ea4f*/
            v4 = 40; /*0x100e9ea52*/
            ZXSnprintf(v13 + 10, 40, "%s", *(const char **)(v21 + 2576)); /*0x100e9ea60*/
          }
          a1[3408] = deal_udt_cag_auth; /*0x100e9ea70*/
          a1[3409] = deal_udt_cag_auth_res; /*0x100e9ea82*/
          if ( (unsigned int)spice_util_get_debug(v5, v4, v6, deal_udt_cag_auth_res, v7, v8) && spice_gtk_log_level < 2 )
            g_log(
              (unsigned int)"GSpice",
              64,
              (unsigned int)"[%-38s:%4d] set kcp cag connect dst: %s:%u",
              (unsigned int)"deal_udt_using_cag",
              5529,
              (_DWORD)v18,
              *v13);
          ikcp_set_auth_data( /*0x100e9eb36*/
            (__int64)a1,
            v14,
            *(_WORD *)(v14 + 4) + 6,
            *(_DWORD *)(v14 + 14),
            *(_DWORD *)(v14 + 10),
            v23,
            1,
            1);
          g_free(v14); /*0x100e9eb3f*/
          return 0; /*0x100e9eb44*/
        }
        else
        {
          g_return_if_fail_warning("GSpice", "deal_udt_using_cag", "pBuffer != NULL"); /*0x100e9e788*/
          return 1; /*0x100e9e78d*/
        }
      }
      else
      {
        return 1; /*0x100e9e733*/
      }
    }
    else
    {
      return (unsigned int)(__int16)sub_100E9EF20(a1, a2); /*0x100e9e5f9*/
    }
  }
  else
  {
    g_return_if_fail_warning("GSpice", "deal_udt_using_cag", "udp_sock != NULL"); /*0x100e9e4e4*/
    return 1; /*0x100e9e4e9*/
  }
}
