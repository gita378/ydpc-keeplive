// 0x131910 @ 0x131910
__int64 __fastcall buildCAGParam(int a1, const std::string *a2, unsigned int a3, __int64 a4)
{
  unsigned int v6; // r12d
  std::string::pointer data; // rdi
  char *v8; // rdx
  unsigned __int64 v9; // rcx
  rsize_t v10; // rbx
  void *v11; // rax
  std::string::pointer v12; // rdx
  std::string::size_type size; // rcx
  char v14; // al
  std::string::size_type v15; // rdx
  std::string::size_type v16; // rdx
  const char *v17; // r9
  const char *v18; // rax
  __int16 v20; // bx
  int v21; // eax
  const char *v22; // rdi
  void **p_data; // rax
  const char *v24; // rsi
  std::string v25; // [rsp+10h] [rbp-170h] BYREF
  std::string v26; // [rsp+28h] [rbp-158h] BYREF
  __int64 v27; // [rsp+40h] [rbp-140h] BYREF
  std::string v28; // [rsp+48h] [rbp-138h] BYREF
  std::string v29; // [rsp+60h] [rbp-120h] BYREF
  std::string v30; // [rsp+78h] [rbp-108h] BYREF
  std::string v31; // [rsp+90h] [rbp-F0h] BYREF
  std::string v32; // [rsp+A8h] [rbp-D8h] BYREF
  std::string v33; // [rsp+C0h] [rbp-C0h] BYREF
  char v34; // [rsp+D8h] [rbp-A8h] BYREF
  _BYTE v35[23]; // [rsp+D9h] [rbp-A7h] BYREF
  unsigned __int8 v36; // [rsp+F0h] [rbp-90h] BYREF
  char v37; // [rsp+F1h] [rbp-8Fh] BYREF
  unsigned __int64 v38; // [rsp+F8h] [rbp-88h]
  void *v39; // [rsp+100h] [rbp-80h]
  std::string v40; // [rsp+108h] [rbp-78h] BYREF
  std::string __str; // [rsp+120h] [rbp-60h] BYREF
  std::string v42; // [rsp+138h] [rbp-48h] BYREF
  __int16 v43; // [rsp+156h] [rbp-2Ah]

  v6 = (unsigned int)a2; /*0x13192a*/
  *(_DWORD *)a4 = a1; /*0x13192d*/
  std::string::basic_string(&v25, a2); /*0x131939*/
  v34 = 24; /*0x13193e*/
  strcpy(v35, "--guest-usr "); /*0x13194f*/
  findKeyFromConnectPara(&v36, &v25, &v34, 12); /*0x131980*/
  if ( (v34 & 1) != 0 ) /*0x13198c*/
    operator delete(*(void **)&v35[15]); /*0x131995*/
  if ( (*(_BYTE *)&v25.__r_.__value_.__s.0 & 1) != 0 ) /*0x1319a1*/
    operator delete(v25.__r_.__value_.__l.__data_); /*0x1319aa*/
  v43 = 0; /*0x1319af*/
  std::string::basic_string(&v28, a2); /*0x1319bf*/
  getPsw(&v42, &v28); /*0x1319d3*/
  if ( (*(_BYTE *)&v28.__r_.__value_.__s.0 & 1) != 0 ) /*0x1319df*/
    operator delete(v28.__r_.__value_.__l.__data_); /*0x1319e8*/
  if ( (v36 & 1) != 0 ) /*0x1319f6*/
  {
    if ( !v38 ) /*0x131a02*/
      goto LABEL_18; /*0x131a02*/
  }
  else if ( !((unsigned __int64)v36 >> 1) ) /*0x131a0c*/
  {
    goto LABEL_18; /*0x131a0c*/
  }
  if ( (*(_BYTE *)&v42.__r_.__value_.__s.0 & 1) == 0 ) /*0x131a13*/
  {
    if ( *(_BYTE *)&v42.__r_.__value_.__s.0 >= 2u ) /*0x131a17*/
    {
      *(_WORD *)(a4 + 4) = v43; /*0x131a1d*/
      data = v42.__r_.__value_.__s.__data_; /*0x131a22*/
      goto LABEL_16; /*0x131a26*/
    }
LABEL_18:
    v6 = 0; /*0x131a70*/
    write_log(3, 0, "buildCAGParam", 6113, "buildCAGParam fail, get usename or password fail."); /*0x131a8f*/
    goto LABEL_47; /*0x131a94*/
  }
  if ( !v42.__r_.__value_.__l.__size_ ) /*0x131a2d*/
    goto LABEL_18; /*0x131a2d*/
  *(_WORD *)(a4 + 4) = v43; /*0x131a33*/
  data = v42.__r_.__value_.__l.__data_; /*0x131a38*/
LABEL_16:
  *(_WORD *)(a4 + 216) = strnlen_s(data, 1024) + 1; /*0x131a3c*/
  if ( (v36 & 1) != 0 ) /*0x131a61*/
  {
    v8 = (char *)v39; /*0x131a63*/
    v9 = v38; /*0x131a67*/
  }
  else
  {
    v9 = (unsigned __int64)v36 >> 1; /*0x131a99*/
    v8 = &v37; /*0x131a9c*/
  }
  ZXMemcpy((void *)(a4 + 152), 0x40u, v8, v9); /*0x131aa8*/
  v10 = *(unsigned __int16 *)(a4 + 216); /*0x131aad*/
  if ( v10 >= 2 ) /*0x131ab9*/
  {
    v11 = operator new[](*(unsigned __int16 *)(a4 + 216)); /*0x131abe*/
    *(_QWORD *)(a4 + 224) = v11; /*0x131ac3*/
    memset_s(v11, v10, 0, v10); /*0x131ad5*/
    if ( (*(_BYTE *)&v42.__r_.__value_.__s.0 & 1) != 0 ) /*0x131af0*/
    {
      v12 = v42.__r_.__value_.__l.__data_; /*0x131af2*/
      size = v42.__r_.__value_.__l.__size_; /*0x131af6*/
    }
    else
    {
      size = (unsigned __int64)*(_BYTE *)&v42.__r_.__value_.__l.0 >> 1; /*0x131afc*/
      v12 = v42.__r_.__value_.__s.__data_; /*0x131aff*/
    }
    ZXMemcpy(*(void **)(a4 + 224), *(unsigned __int16 *)(a4 + 216), v12, size); /*0x131b03*/
  }
  HideSensitiveInfo(&v42); /*0x131b0c*/
  *(_WORD *)&__str.__r_.__value_.__l.0 = 0; /*0x131b11*/
  *(_WORD *)&v40.__r_.__value_.__l.0 = 0; /*0x131b17*/
  std::string::basic_string(&v29, a2); /*0x131b27*/
  getDestipAndPortFromConnectType(&v29); /*0x131b3e*/
  if ( (*(_BYTE *)&v29.__r_.__value_.__s.0 & 1) != 0 ) /*0x131b4a*/
    operator delete(v29.__r_.__value_.__l.__data_); /*0x131b53*/
  std::string::basic_string(&v31, &__str); /*0x131b63*/
  std::string::basic_string(&v26, &v40); /*0x131b73*/
  v14 = *(_BYTE *)&v31.__r_.__value_.__s.0 & 1; /*0x131b81*/
  if ( (*(_BYTE *)&v31.__r_.__value_.__s.0 & 1) != 0 ) /*0x131b83*/
    v15 = v31.__r_.__value_.__l.__size_; /*0x131b85*/
  else
    v15 = (unsigned __int64)*(_BYTE *)&v31.__r_.__value_.__l.0 >> 1; /*0x131b8e*/
  if ( v15 ) /*0x131b9b*/
  {
    if ( (*(_BYTE *)&v26.__r_.__value_.__s.0 & 1) != 0 ) /*0x131ba0*/
      v16 = v26.__r_.__value_.__l.__size_; /*0x131ba2*/
    else
      v16 = (unsigned __int64)*(_BYTE *)&v26.__r_.__value_.__l.0 >> 1; /*0x131bb8*/
    LOBYTE(v6) = v16 != 0; /*0x131bbe*/
    if ( (*(_BYTE *)&v26.__r_.__value_.__s.0 & 1) != 0 ) /*0x131bc5*/
      goto LABEL_37; /*0x131bc5*/
  }
  else
  {
    v6 = 0; /*0x131bab*/
    if ( (*(_BYTE *)&v26.__r_.__value_.__s.0 & 1) != 0 ) /*0x131bb1*/
    {
LABEL_37:
      operator delete(v26.__r_.__value_.__l.__data_); /*0x131bc7*/
      v14 = *(_BYTE *)&v31.__r_.__value_.__s.0 & 1; /*0x131bd9*/
    }
  }
  if ( v14 ) /*0x131bdd*/
    operator delete(v31.__r_.__value_.__l.__data_); /*0x131be6*/
  if ( (*(_BYTE *)&__str.__r_.__value_.__s.0 & 1) != 0 ) /*0x131bef*/
  {
    v17 = __str.__r_.__value_.__l.__data_; /*0x131bf5*/
    if ( (*(_BYTE *)&v40.__r_.__value_.__s.0 & 1) == 0 ) /*0x131bfd*/
      goto LABEL_42; /*0x131bfd*/
  }
  else
  {
    v17 = __str.__r_.__value_.__s.__data_; /*0x131c89*/
    if ( (*(_BYTE *)&v40.__r_.__value_.__s.0 & 1) == 0 ) /*0x131c91*/
    {
LABEL_42:
      v18 = v40.__r_.__value_.__s.__data_; /*0x131c03*/
      if ( !(_BYTE)v6 ) /*0x131c0a*/
        goto LABEL_43; /*0x131c0a*/
      goto LABEL_54; /*0x131c0a*/
    }
  }
  v18 = v40.__r_.__value_.__l.__data_; /*0x131c97*/
  if ( !(_BYTE)v6 ) /*0x131c9e*/
  {
LABEL_43:
    write_log( /*0x131c10*/
      3,
      0,
      "buildCAGParam",
      6132,
      "judgeConnectTypeCag,judgeDestIpOrPortExist false,strDestIp:%s,strDestPort:%s",
      v17,
      v18);
    if ( (*(_BYTE *)&v40.__r_.__value_.__s.0 & 1) == 0 ) /*0x131c39*/
      goto LABEL_45; /*0x131c39*/
    goto LABEL_44; /*0x131c39*/
  }
LABEL_54:
  write_log( /*0x131ca4*/
    3,
    0,
    "buildCAGParam",
    6135,
    "getDestipAndPortFromConnectType success,strDestIp:%s,strDestPort:%s",
    v17,
    v18);
  std::string::basic_string(&v30, &v40); /*0x131cd4*/
  v20 = stringToInt(&v30, 1); /*0x131cea*/
  if ( (*(_BYTE *)&v30.__r_.__value_.__s.0 & 1) != 0 ) /*0x131cf3*/
    operator delete(v30.__r_.__value_.__l.__data_); /*0x131cfc*/
  if ( a3 <= 4 && (v21 = 21, _bittest(&v21, a3)) ) /*0x131d0c*/
  {
    std::string::basic_string(&v32, &__str); /*0x131d1d*/
    if ( (*(_BYTE *)&v32.__r_.__value_.__s.0 & 1) != 0 ) /*0x131d29*/
      v22 = v32.__r_.__value_.__l.__data_; /*0x131d2b*/
    else
      v22 = v32.__r_.__value_.__s.__data_; /*0x131d34*/
    v27 = inet_addr(v22); /*0x131d42*/
    ZXMemcpy((void *)(a4 + 24), 0x10u, &v27, 8u); /*0x131d5e*/
    *(_BYTE *)(a4 + 39) = 0; /*0x131d63*/
    if ( (*(_BYTE *)&v32.__r_.__value_.__s.0 & 1) != 0 ) /*0x131d6f*/
    {
      p_data = (void **)&v32.__r_.__value_.__l.__data_; /*0x131d75*/
LABEL_70:
      operator delete(*p_data); /*0x131def*/
    }
  }
  else
  {
    std::string::basic_string(&v33, &__str); /*0x131d89*/
    *(_BYTE *)(a4 + 89) |= 1u; /*0x131d8e*/
    if ( (*(_BYTE *)&v33.__r_.__value_.__s.0 & 1) != 0 ) /*0x131d9a*/
      v24 = v33.__r_.__value_.__l.__data_; /*0x131d9c*/
    else
      v24 = v33.__r_.__value_.__s.__data_; /*0x131da5*/
    if ( inet_pton(30, v24, (void *)(a4 + 24)) <= 0 ) /*0x131dbc*/
      write_log(3, 0, "getCagParaIpv6", 6010, "getCagParaIpv6 inet_pton fail"); /*0x131dda*/
    if ( (*(_BYTE *)&v33.__r_.__value_.__s.0 & 1) != 0 ) /*0x131de6*/
    {
      p_data = (void **)&v33.__r_.__value_.__l.__data_; /*0x131de8*/
      goto LABEL_70; /*0x131de8*/
    }
  }
  *(_WORD *)(a4 + 40) = v20; /*0x131df7*/
  if ( (*(_BYTE *)&v40.__r_.__value_.__s.0 & 1) != 0 ) /*0x131e00*/
LABEL_44:
    operator delete(v40.__r_.__value_.__l.__data_); /*0x131c3b*/
LABEL_45:
  if ( (*(_BYTE *)&__str.__r_.__value_.__s.0 & 1) != 0 ) /*0x131c48*/
    operator delete(__str.__r_.__value_.__l.__data_); /*0x131c4e*/
LABEL_47:
  if ( (*(_BYTE *)&v42.__r_.__value_.__s.0 & 1) != 0 ) /*0x131c57*/
    operator delete(v42.__r_.__value_.__l.__data_); /*0x131c5d*/
  if ( (v36 & 1) != 0 ) /*0x131c69*/
    operator delete(v39); /*0x131c6f*/
  return v6; /*0x131c77*/
}
