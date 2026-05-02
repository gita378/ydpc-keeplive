// 0x47d0 @ 0x47d0
__int64 __fastcall send_access_gateway_local_key(__int64 a1, int a2)
{
  int v2; // r8d
  int v3; // r9d
  const char *v4; // rdx
  int v5; // r8d
  int v6; // r9d
  int v7; // ecx
  int v8; // r8d
  int v9; // r9d
  int v10; // r8d
  int v11; // r9d
  char *v13; // [rsp+38h] [rbp-68h]
  int v14; // [rsp+44h] [rbp-5Ch]
  _DWORD __b[2]; // [rsp+48h] [rbp-58h] BYREF
  unsigned int sock_error; // [rsp+50h] [rbp-50h]
  int v17; // [rsp+54h] [rbp-4Ch]
  __int64 v18; // [rsp+58h] [rbp-48h]
  _DWORD v20[12]; // [rsp+68h] [rbp-38h] BYREF

  v18 = a1; /*0x47eb*/
  v17 = a2; /*0x47ef*/
  sock_error = 0; /*0x47f2*/
  strcpy((char *)__b, "ZTEC,"); /*0x4815*/
  memset(v20, 0, 0x2Cu); /*0x482d*/
  v20[0] = *(unsigned __int16 *)(a1 + 4) + 100; /*0x483d*/
  v4 = "uac"; /*0x4852*/
  if ( *(_WORD *)(a1 + 4) == 1 ) /*0x4859*/
    v4 = "radius"; /*0x4859*/
  write_log((unsigned int)"send_access_gateway_local_key", 846, (unsigned int)"auth type is %s", (_DWORD)v4, v2, v3); /*0x487d*/
  v20[7] |= 1u; /*0x4888*/
  v20[7] |= 2u; /*0x4891*/
  v20[7] |= *(unsigned __int8 *)(v18 + 88) << 16; /*0x48a2*/
  v20[7] |= *(unsigned __int8 *)(v18 + 90) << 24; /*0x48b3*/
  v20[1] = v17; /*0x48b9*/
  if ( *(_WORD *)(v18 + 4) == 1 ) /*0x48cd*/
  {
    v20[2] = 220; /*0x48d3*/
  }
  else
  {
    v14 = 0; /*0x48df*/
    if ( *(_WORD *)(v18 + 216) ) /*0x48ea*/
    {
      if ( *(_QWORD *)(v18 + 224) ) /*0x48fe*/
      {
        v14 = *(unsigned __int16 *)(v18 + 216) + 1; /*0x491a*/
        if ( v14 % 16 ) /*0x4926*/
          v14 = 16 * (v14 / 16 + 1); /*0x4942*/
      }
    }
    v20[2] = v14 + 126; /*0x4954*/
  }
  v13 = (char *)malloc(0x32u); /*0x496b*/
  if ( v13 )
  {
    ZXMemcpy(&v20[3], 16, v18 + 8, 16); /*0x49c5*/
    ZXMemcpy(v13, 50, __b, 6); /*0x49e1*/
    ZXMemcpy(v13 + 6, 44, v20, 44); /*0x4a1f*/
    if ( send(*(_DWORD *)v18, v13, 0x32u, 0) > 0 )
    {
      write_log( /*0x4a88*/
        (unsigned int)"send_access_gateway_local_key",
        882,
        (unsigned int)"send client key to cag success",
        v7,
        v8,
        v9);
    }
    else
    {
      sock_error = get_sock_error(); /*0x4a4e*/
      write_log(
        (unsigned int)"send_access_gateway_local_key",
        880,
        (unsigned int)"ERROR: send client key to cag failed(%d)",
        sock_error,
        v10,
        v11);
    }
    free(v13); /*0x4a91*/
    return sock_error; /*0x4a99*/
  }
  else
  {
    write_log((unsigned int)"send_access_gateway_local_key", 870, (unsigned int)"ERROR: malloc failed", 0, v5, v6);
    return 1002; /*0x4993*/
  }
}
