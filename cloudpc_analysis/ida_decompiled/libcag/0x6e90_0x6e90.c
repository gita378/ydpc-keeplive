// 0x6e90 @ 0x6e90
__int64 __fastcall tn_deal_aes_code(__int64 a1, unsigned int a2, __int64 a3, int a4, int a5, char a6, int a7)
{
  unsigned int v8; // [rsp+0h] [rbp-210h]
  __int64 v9; // [rsp+0h] [rbp-210h]
  int v10; // [rsp+8h] [rbp-208h]
  __int64 v11; // [rsp+8h] [rbp-208h]
  int v12; // [rsp+10h] [rbp-200h]
  __int64 v13; // [rsp+10h] [rbp-200h]
  unsigned int v14; // [rsp+18h] [rbp-1F8h]
  __int64 v15; // [rsp+18h] [rbp-1F8h]
  __int64 v16; // [rsp+38h] [rbp-1D8h]
  int v17; // [rsp+50h] [rbp-1C0h]
  unsigned int v18; // [rsp+68h] [rbp-1A8h]
  _BYTE v19[12]; // [rsp+6Ch] [rbp-1A4h]
  AES_KEY key; // [rsp+78h] [rbp-198h] BYREF
  char v21; // [rsp+16Fh] [rbp-A1h]
  int v22; // [rsp+170h] [rbp-A0h]
  int v23; // [rsp+174h] [rbp-9Ch]
  __int64 v24; // [rsp+178h] [rbp-98h]
  unsigned int v25; // [rsp+184h] [rbp-8Ch]
  __int64 v26; // [rsp+188h] [rbp-88h]
  unsigned __int8 ivec[32]; // [rsp+190h] [rbp-80h] BYREF
  unsigned __int8 userKey[48]; // [rsp+1B0h] [rbp-60h] BYREF

  v26 = a1; /*0x6eb8*/
  v25 = a2; /*0x6ebf*/
  v24 = a3; /*0x6ec5*/
  v23 = a4; /*0x6ecc*/
  v22 = a5; /*0x6ed2*/
  v21 = a6; /*0x6ed9*/
  *(_DWORD *)&v19[8] = 0; /*0x6ee0*/
  *(_QWORD *)v19 = a4 & 0xABACACAB; /*0x6ef7*/
  v18 = a5 | 0x98979798; /*0x6f09*/
  v17 = (a7 >> 8) & 1; /*0x6f43*/
  v8 = (a4 & 0xABACACAB) >> 24; /*0x6fe7*/
  v10 = (unsigned __int8)((unsigned __int16)(a5 | 0x9798) >> 8); /*0x6feb*/
  v12 = (unsigned __int8)((a5 | 0x98979798) >> 16); /*0x6ff0*/
  v14 = (a5 | 0x98979798) >> 24; /*0x6ff4*/
  HIDWORD(v16) = ZXMemset(&key, 244, 0, 244); /*0x6ff9*/
  ZXSnprintf( /*0x7001*/
    (unsigned int)ivec,
    20,
    (unsigned int)"02x%02X%02X%02x%02X%02x%02x%02X",
    v19[2],
    v19[0],
    v19[1],
    v8,
    v10,
    v12,
    v14);
  LODWORD(v16) = HIBYTE(v18); /*0x7078*/
  LODWORD(v9) = HIBYTE(v18); /*0x708d*/
  LODWORD(v11) = BYTE2(v18); /*0x7090*/
  LODWORD(v13) = BYTE1(v18); /*0x7095*/
  LODWORD(v15) = v19[3]; /*0x7099*/
  ZXSnprintf( /*0x70af*/
    (unsigned int)userKey,
    40,
    (unsigned int)"%08x%08x%02x%02x%02x%02x%02x%02x%02x%02x",
    v23,
    v22,
    (unsigned __int8)v18,
    v9,
    v11,
    v13,
    v15,
    v19[1],
    v19[0],
    v19[2],
    v16);
  userKey[39] = 0; /*0x70b4*/
  if ( v21 ) /*0x70bf*/
  {
    AES_set_decrypt_key(userKey, (unsigned __int8)a7 << 7, &key); /*0x71af*/
    while ( *(_QWORD *)&v19[4] + 16LL <= (unsigned __int64)v25 ) /*0x71cc*/
    {
      if ( v17 ) /*0x71d9*/
        AES_cbc_encrypt( /*0x7247*/
          (const unsigned __int8 *)(*(_QWORD *)&v19[4] + v26),
          (unsigned __int8 *)(*(_QWORD *)&v19[4] + v24),
          0x10u,
          &key,
          ivec,
          0);
      else
        AES_decrypt( /*0x7208*/
          (const unsigned __int8 *)(*(_QWORD *)&v19[4] + v26),
          (unsigned __int8 *)(*(_QWORD *)&v19[4] + v24),
          &key);
      *(_QWORD *)&v19[4] += 16LL; /*0x7259*/
    }
  }
  else
  {
    AES_set_encrypt_key(userKey, (unsigned __int8)a7 << 7, &key); /*0x70db*/
    while ( *(_QWORD *)&v19[4] + 16LL <= (unsigned __int64)v25 ) /*0x70f8*/
    {
      if ( v17 ) /*0x7105*/
        AES_cbc_encrypt( /*0x7176*/
          (const unsigned __int8 *)(*(_QWORD *)&v19[4] + v26),
          (unsigned __int8 *)(*(_QWORD *)&v19[4] + v24),
          0x10u,
          &key,
          ivec,
          1);
      else
        AES_encrypt( /*0x7134*/
          (const unsigned __int8 *)(*(_QWORD *)&v19[4] + v26),
          (unsigned __int8 *)(*(_QWORD *)&v19[4] + v24),
          &key);
      *(_QWORD *)&v19[4] += 16LL; /*0x7188*/
    }
  }
  return __stack_chk_guard; /*0x7281*/
}
