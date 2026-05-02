// 0x100e8f4c0 @ 0x100e8f4c0
__int64 __fastcall proxy_kcp_data_read(__int64 a1, __int64 a2, __int64 a3, __int64 a4, __int64 a5, __int64 a6)
{
  int v6; // r9d
  int v7; // edx
  __int64 v8; // rdi
  __int64 v9; // rsi
  __int64 v10; // rdx
  __int64 v11; // rcx
  __int64 v12; // r8
  __int64 v13; // r9
  _WORD *v15; // [rsp+18h] [rbp-A8h]
  bool v16; // [rsp+27h] [rbp-99h]
  __int64 v17; // [rsp+28h] [rbp-98h]
  _WORD *v18; // [rsp+30h] [rbp-90h]
  unsigned __int16 v19; // [rsp+3Eh] [rbp-82h]
  __int64 v20; // [rsp+40h] [rbp-80h]
  int v21; // [rsp+48h] [rbp-78h]
  int v22; // [rsp+4Ch] [rbp-74h] BYREF
  _WORD *v23; // [rsp+50h] [rbp-70h]
  _WORD v24[16]; // [rsp+58h] [rbp-68h] BYREF
  unsigned int v25; // [rsp+78h] [rbp-48h]
  int v26; // [rsp+7Ch] [rbp-44h]
  __int64 v27; // [rsp+80h] [rbp-40h]
  unsigned __int16 v29; // [rsp+8Eh] [rbp-32h]
  __int64 v30; // [rsp+90h] [rbp-30h]
  __int64 v31; // [rsp+98h] [rbp-28h]
  __int64 v32; // [rsp+A0h] [rbp-20h]
  _WORD __b[8]; // [rsp+A8h] [rbp-18h] BYREF

  v27 = a1; /*0x100e8f4d9*/
  if ( a1 ) /*0x100e8f4e2*/
  {
    v26 = 100; /*0x100e8f534*/
    v16 = 0; /*0x100e8f547*/
    if ( *(_QWORD *)(v27 + 176) ) /*0x100e8f53f*/
      v16 = *(_BYTE *)(*(_QWORD *)(v27 + 176) + 21060LL) != 0; /*0x100e8f56b*/
    v25 = v16; /*0x100e8f57e*/
    memset(__b, 0, sizeof(__b)); /*0x100e8f595*/
    memset(v24, 0, 0x1Cu); /*0x100e8f5ac*/
    if ( v16 ) /*0x100e8f579*/
      v15 = v24; /*0x100e8f5bf*/
    else
      v15 = __b; /*0x100e8f5cf*/
    v23 = v15; /*0x100e8f5dd*/
    v7 = 16; /*0x100e8f5ec*/
    if ( v25 ) /*0x100e8f5f1*/
      v7 = 28; /*0x100e8f5f1*/
    v22 = v7; /*0x100e8f5f4*/
    v21 = 0; /*0x100e8f5f7*/
    while ( (unsigned int)++v21 < 0x64 ) /*0x100e8f604*/
    {
      HIDWORD(v20) = sub_100E8F860(*(unsigned int *)(v27 + 24), v27 + 432, 2048, v23, &v22); /*0x100e8f636*/
      if ( v20 < 0 ) /*0x100e8f63d*/
        break; /*0x100e8f63d*/
      if ( SHIDWORD(v20) >= 21 ) /*0x100e8f64c*/
      {
        LODWORD(v20) = ikcp_getconv((unsigned int *)(v27 + 432)); /*0x100e8f669*/
        if ( (v20 & 0x80000000) != 0 ) /*0x100e8f677*/
        {
          if ( v25 ) /*0x100e8f69a*/
          {
            v19 = sub_100E8F9C0(v24[1]); /*0x100e8f6bb*/
            v18 = &v24[4]; /*0x100e8f6cd*/
          }
          else
          {
            v19 = sub_100E8F9C0(__b[1]); /*0x100e8f6f4*/
            v18 = &__b[2]; /*0x100e8f706*/
          }
          v8 = *(unsigned int *)(v27 + 24); /*0x100e8f711*/
          v9 = v27 + 69200; /*0x100e8f72f*/
          v17 = sub_100E8F9E0(v8, v27 + 69200, v25, v19, v18); /*0x100e8f73a*/
          if ( v17 ) /*0x100e8f749*/
          {
            v32 = v27; /*0x100e8f7b3*/
            v31 = v20; /*0x100e8f7ba*/
            v30 = v17; /*0x100e8f7bd*/
            v29 = v19; /*0x100e8f7c1*/
            if ( ikcp_be_spical_conv(v20) ) /*0x100e8f7c8*/
              sub_100EA1710(v32, HIDWORD(v31), (unsigned int)v31, v30, v29); /*0x100e8f7e9*/
            else
              deal_kcp_common_data(v32, HIDWORD(v31), v31, v30, v29); /*0x100e8f806*/
          }
          else if ( (unsigned int)spice_util_get_debug(v8, v9, v10, v11, v12, v13) ) /*0x100e8f754*/
          {
            g_log( /*0x100e8f78c*/
              (unsigned int)"GSpice",
              8,
              (unsigned int)"[%-38s:%4d] fd:%d update_ip_cache failed.",
              (unsigned int)"proxy_kcp_data_read",
              7883,
              *(_DWORD *)(v27 + 24));
          }
        }
      }
    }
    sub_100E8FD30(v27); /*0x100e8f814*/
    return 0; /*0x100e8f819*/
  }
  else
  {
    if ( (unsigned int)spice_util_get_debug(0, a2, a3, a4, a5, a6) ) /*0x100e8f4ed*/
      g_log( /*0x100e8f51d*/
        (unsigned int)"GSpice",
        8,
        (unsigned int)"[%-38s:%4d] [QUIC] Invalid socket pointer",
        (unsigned int)"proxy_kcp_data_read",
        7818,
        v6);
    return 1; /*0x100e8f527*/
  }
}
