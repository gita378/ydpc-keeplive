// 0x1cff0 @ 0x1cff0
_DWORD *__fastcall ClientManager::ConnectStrAesEncode(__int64 a1, unsigned __int8 *a2)
{
  _BYTE *v2; // r14
  __int64 v3; // rax
  __int64 v4; // rbx
  __int64 v5; // rax
  __int64 v6; // rax
  __int64 v7; // rax
  __int64 v8; // rax
  unsigned int v9; // eax
  unsigned __int64 v10; // rbx
  std::string::size_type v11; // r15
  std::string::size_type size; // rbx
  unsigned __int8 *v13; // r14
  __int64 v14; // rbx
  unsigned __int64 v15; // rax
  unsigned __int64 v16; // rax
  int v17; // ecx
  int v18; // edx
  int v19; // r12d
  _DWORD *v20; // r14
  int v21; // r12d
  __int64 v22; // rax
  rsize_t v23; // rbx
  size_t v24; // r15
  unsigned __int8 *v25; // rax
  unsigned __int8 *v26; // r13
  unsigned int v27; // r14d
  unsigned __int64 v28; // rcx
  unsigned __int64 v29; // rcx
  const void *v30; // rdx
  unsigned __int8 *v31; // rax
  unsigned int v32; // r12d
  unsigned __int8 *v33; // r15
  _DWORD *v34; // rax
  char v36; // [rsp+10h] [rbp-A0h] BYREF
  _BYTE v37[23]; // [rsp+11h] [rbp-9Fh]
  std::string v38; // [rsp+28h] [rbp-88h] BYREF
  unsigned int v39[2]; // [rsp+40h] [rbp-70h]
  unsigned __int8 *v40; // [rsp+48h] [rbp-68h]
  unsigned int v41[2]; // [rsp+50h] [rbp-60h]
  std::string __str; // [rsp+58h] [rbp-58h] BYREF
  _QWORD v43[2]; // [rsp+70h] [rbp-40h]

  v40 = a2; /*0x1d004*/
  v2 = operator new[](7u); /*0x1d020*/
  v2[6] = 0; /*0x1d023*/
  v3 = Random(10); /*0x1d02c*/
  v4 = 9; /*0x1d034*/
  if ( (unsigned int)v3 >= 9 ) /*0x1d039*/
    v3 = 9; /*0x1d039*/
  *v2 = a1123456789[v3]; /*0x1d047*/
  v5 = Random(10); /*0x1d04f*/
  if ( (unsigned int)v5 >= 9 ) /*0x1d057*/
    v5 = 9; /*0x1d057*/
  v2[1] = a1123456789[v5]; /*0x1d05e*/
  v6 = Random(10); /*0x1d067*/
  if ( (unsigned int)v6 >= 9 ) /*0x1d06f*/
    v6 = 9; /*0x1d06f*/
  v2[2] = a1123456789[v6]; /*0x1d076*/
  v7 = Random(10); /*0x1d07f*/
  if ( (unsigned int)v7 >= 9 ) /*0x1d087*/
    v7 = 9; /*0x1d087*/
  v2[3] = a1123456789[v7]; /*0x1d08e*/
  v8 = Random(10); /*0x1d097*/
  if ( (unsigned int)v8 >= 9 ) /*0x1d09f*/
    v8 = 9; /*0x1d09f*/
  v2[4] = a1123456789[v8]; /*0x1d0a6*/
  v9 = Random(10); /*0x1d0af*/
  if ( v9 < 9 ) /*0x1d0b7*/
    v4 = v9; /*0x1d0b7*/
  v2[5] = a1123456789[v4]; /*0x1d0be*/
  CharToString(&v36); /*0x1d0cc*/
  v10 = (unsigned __int8)v36; /*0x1d0d1*/
  v43[0] = *(_QWORD *)v37; /*0x1d0e6*/
  *(_QWORD *)((char *)v43 + 7) = *(_QWORD *)&v37[7]; /*0x1d0ea*/
  v11 = *(_QWORD *)&v37[15]; /*0x1d0ee*/
  operator delete[](v2); /*0x1d0f8*/
  __str.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)v10; /*0x1d0fd*/
  *(std::string::size_type *)((char *)__str.__r_.__value_.__r.__words + 1) = v43[0]; /*0x1d108*/
  __str.__r_.__value_.__l.__size_ = *(_QWORD *)((char *)v43 + 7); /*0x1d10c*/
  __str.__r_.__value_.__r.__words[2] = v11; /*0x1d110*/
  if ( (v10 & 1) != 0 ) /*0x1d117*/
    size = __str.__r_.__value_.__l.__size_; /*0x1d119*/
  else
    size = v10 >> 1; /*0x1d11f*/
  v13 = v40; /*0x1d125*/
  if ( size ) /*0x1d129*/
  {
    std::string::basic_string(&v38, &__str); /*0x1d136*/
    v14 = (unsigned int)stringToInt(&v38, 0); /*0x1d149*/
    if ( (*(_BYTE *)&v38.__r_.__value_.__s.0 & 1) != 0 ) /*0x1d152*/
      operator delete(v38.__r_.__value_.__l.__data_); /*0x1d158*/
  }
  else
  {
    v14 = 1; /*0x1d15f*/
  }
  v15 = *v13; /*0x1d164*/
  *(_QWORD *)v39 = v14; /*0x1d16a*/
  if ( (v15 & 1) != 0 ) /*0x1d16e*/
    LODWORD(v16) = *((_DWORD *)v13 + 2); /*0x1d170*/
  else
    v16 = v15 >> 1; /*0x1d176*/
  v17 = v16 + 15; /*0x1d179*/
  if ( (v16 & 0x80000000) == 0LL ) /*0x1d17e*/
    v17 = v16; /*0x1d17e*/
  v18 = v16 - (v17 & 0xFFFFFFF0); /*0x1d186*/
  v19 = 16 - v18; /*0x1d18e*/
  v20 = 0; /*0x1d191*/
  if ( v18 <= 0 ) /*0x1d196*/
    v19 = 0; /*0x1d196*/
  v21 = v16 + v19; /*0x1d19a*/
  v22 = (unsigned int)(2 * v21); /*0x1d19d*/
  *(_QWORD *)v41 = v22; /*0x1d1a1*/
  v23 = (int)v22; /*0x1d1a5*/
  v24 = -1; /*0x1d1ab*/
  if ( v21 >= 0 ) /*0x1d1b2*/
    v24 = (int)v22; /*0x1d1b2*/
  v25 = (unsigned __int8 *)operator new[](v24, &std::nothrow); /*0x1d1c0*/
  if ( v25 ) /*0x1d1c8*/
  {
    v26 = v25; /*0x1d1ce*/
    memset_s(v25, v23, 0, v23); /*0x1d1dc*/
    v27 = v41[0]; /*0x1d1e1*/
    v28 = *v40; /*0x1d1e9*/
    if ( (v28 & 1) != 0 ) /*0x1d1ef*/
    {
      v29 = *((_QWORD *)v40 + 1); /*0x1d1f1*/
      v30 = (const void *)*((_QWORD *)v40 + 2); /*0x1d1f5*/
    }
    else
    {
      v30 = v40 + 1; /*0x1d1fb*/
      v29 = v28 >> 1; /*0x1d1fe*/
    }
    ZXMemcpy(v26, v23, v30, v29); /*0x1d207*/
    if ( v21 > 0 ) /*0x1d20f*/
      v26[v27 - 1] = 0; /*0x1d215*/
    v31 = (unsigned __int8 *)operator new[](v24, &std::nothrow); /*0x1d225*/
    v32 = v39[0]; /*0x1d22d*/
    if ( v31 ) /*0x1d231*/
    {
      v33 = v31; /*0x1d237*/
      memset_s(v31, v23, 0, v23); /*0x1d245*/
      write_log(1, 0, "ConnectStrAesEncode", 1186, "nRandom:%d len:%d", v32, v27); /*0x1d26d*/
      CBC_AESEncryptStr(v26, v27, v33, v32, v32 - 1, 1); /*0x1d289*/
      v34 = operator new(0x10u, &std::nothrow); /*0x1d29a*/
      if ( v34 ) /*0x1d2a2*/
      {
        v20 = v34; /*0x1d2a4*/
        *v34 = v32; /*0x1d2a7*/
        v34[1] = v41[0]; /*0x1d2ae*/
        *((_QWORD *)v34 + 1) = v33; /*0x1d2b2*/
      }
      else
      {
        operator delete[](v26); /*0x1d2c0*/
        v20 = 0; /*0x1d2c5*/
        v26 = v33; /*0x1d2c8*/
      }
    }
    else
    {
      v20 = 0; /*0x1d2b8*/
    }
    operator delete[](v26); /*0x1d2ce*/
  }
  if ( (*(_BYTE *)&__str.__r_.__value_.__s.0 & 1) != 0 ) /*0x1d2d7*/
    operator delete(__str.__r_.__value_.__l.__data_); /*0x1d2dd*/
  return v20; /*0x1d2f5*/
}
