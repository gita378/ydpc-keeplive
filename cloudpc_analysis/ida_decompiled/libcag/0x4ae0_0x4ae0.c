// 0x4ae0 @ 0x4ae0
__int64 __fastcall recv_access_gateway_key(unsigned int a1, _DWORD *a2, int *a3, unsigned int a4)
{
  int v4; // ecx
  int v5; // r8d
  int v6; // r9d
  int v7; // ecx
  int v8; // r8d
  int v9; // r9d
  int v10; // eax
  int v11; // eax
  int v12; // esi
  _WORD __b[6]; // [rsp+10h] [rbp-60h] BYREF
  unsigned int v15; // [rsp+1Ch] [rbp-54h]
  int *v16; // [rsp+20h] [rbp-50h]
  _DWORD *v17; // [rsp+28h] [rbp-48h]
  unsigned int v18; // [rsp+30h] [rbp-40h]
  _DWORD v20[12]; // [rsp+38h] [rbp-38h] BYREF

  v18 = a1; /*0x4af8*/
  v17 = a2; /*0x4afb*/
  v16 = a3; /*0x4aff*/
  v15 = a4; /*0x4b03*/
  memset(__b, 0, 6u); /*0x4b17*/
  memset(v20, 0, 0x2Cu); /*0x4b2b*/
  write_log((unsigned int)"recv_access_gateway_key", 893, (unsigned int)"recv_access_gateway_key start!!!", v4, v5, v6); /*0x4b45*/
  if ( (int)receive_data_by_socket(v18, __b, 6, v15) == 6
    && (v7 = __b[2], __b[2] == 44)
    && (v10 = receive_data_by_socket(v18, v20, 44, v15), v8 = 44, v10 == 44) )
  {
    v11 = 0; /*0x4ba7*/
    *v17 = v20[1]; /*0x4bb0*/
    v12 = 1; /*0x4bc0*/
    if ( (v20[7] & 1) != 0 ) /*0x4bc5*/
      v12 = 2; /*0x4bc5*/
    *v16 = v12; /*0x4bcc*/
    if ( (v20[7] & 2) != 0 ) /*0x4bdc*/
      v11 = 256; /*0x4bdc*/
    *v16 |= v11; /*0x4be5*/
    write_log( /*0x4c06*/
      (unsigned int)"recv_access_gateway_key",
      899,
      (unsigned int)"recv server key from cag success, key = %u, aes_flag = %d",
      v20[1],
      *v16,
      v9);
    return 0; /*0x4c0b*/
  }
  else
  {
    write_log(
      (unsigned int)"recv_access_gateway_key",
      903,
      (unsigned int)"ERROR: recv server key from cag failed",
      v7,
      v8,
      v9);
    return 1010; /*0x4c36*/
  }
}
