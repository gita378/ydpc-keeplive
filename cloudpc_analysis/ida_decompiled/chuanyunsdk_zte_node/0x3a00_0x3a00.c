// 0x3a00 @ 0x3a00
__int64 __fastcall runSimpleAsyncWorker(__int64 a1)
{
  __int128 v2; // rax
  int v3; // eax
  std::string::size_type v4; // rax
  __int64 v5; // rax
  __int64 v6; // rdx
  __int64 v7; // rax
  __int64 v8; // rdx
  __int64 v9; // rax
  std::string::value_type *v10; // rsi
  std::string::size_type v11; // rdx
  __int64 v12; // rax
  __int64 v13; // rdx
  __int64 v14; // rax
  __int64 v15; // rdx
  __int64 v16; // rax
  __int64 v17; // rdx
  __int128 v18; // rax
  __int64 v19; // rax
  __int64 v20; // rdx
  unsigned __int64 v21; // rsi
  __int128 v22; // rax
  __int64 v23; // r15
  __int64 v24; // rdx
  __int64 v25; // r14
  const std::locale::facet *v26; // rax
  char v27; // r12
  __int64 v28; // rax
  std::string::value_type *v29; // rsi
  std::string::size_type v30; // rdx
  __int64 v31; // r12
  const std::locale::facet *v32; // rax
  char v33; // r14
  __int64 v34; // r14
  const char *v35; // r12
  size_t v36; // rax
  __int64 v37; // r14
  const std::locale::facet *v38; // rax
  char v39; // r15
  char *v40; // r14
  __int64 v41; // rdx
  __int64 v42; // rdx
  std::string *v43; // rdi
  std::string *v44; // rdi
  std::string *v45; // rdi
  std::string *v46; // rdi
  std::string *v47; // rdi
  std::string *v48; // rdi
  __int64 v49; // rbx
  std::string::size_type __sz[2]; // [rsp+0h] [rbp-110h]
  void *__p[4]; // [rsp+10h] [rbp-100h] BYREF
  std::string::size_type v53[2]; // [rsp+30h] [rbp-E0h] BYREF
  char *__s[4]; // [rsp+40h] [rbp-D0h] BYREF
  int v55; // [rsp+60h] [rbp-B0h]
  std::string::size_type v56[2]; // [rsp+68h] [rbp-A8h]
  std::string::value_type *v57; // [rsp+78h] [rbp-98h]
  int v58; // [rsp+80h] [rbp-90h]
  __int128 v59; // [rsp+90h] [rbp-80h] BYREF
  std::string::size_type v60[2]; // [rsp+A8h] [rbp-68h] BYREF
  std::string::value_type *v61; // [rsp+B8h] [rbp-58h]
  __int64 v62; // [rsp+C0h] [rbp-50h] BYREF
  __int64 v63; // [rsp+C8h] [rbp-48h]
  _OWORD v64[4]; // [rsp+D0h] [rbp-40h] BYREF

  v59 = 0; /*0x3a1a*/
  *(_OWORD *)v56 = 0; /*0x3a1e*/
  v57 = 0; /*0x3a25*/
  *(_OWORD *)__sz = 0; /*0x3a30*/
  memset(__p, 0, sizeof(__p)); /*0x3a37*/
  *(_OWORD *)v53 = 0; /*0x3a45*/
  memset(__s, 0, sizeof(__s)); /*0x3a4c*/
  *(_QWORD *)&v2 = *(_QWORD *)(a1 + 8); /*0x3a5f*/
  if ( *(_QWORD *)(a1 + 32) ) /*0x3a5a*/
  {
    *((_QWORD *)&v2 + 1) = **(_QWORD **)(a1 + 40); /*0x3a69*/
  }
  else
  {
    v60[0] = *(_QWORD *)(a1 + 8); /*0x3a6e*/
    *(_QWORD *)&v2 = Napi::Env::Undefined((Napi::Env *)v60); /*0x3a76*/
  }
  v64[0] = v2; /*0x3a82*/
  Napi::String::Utf8Value((Napi::String *)v60); /*0x3a92*/
  if ( (v60[0] & 1) != 0 )
  {
    v4 = v60[1]; /*0x3aec*/
    if ( v60[1] == 7 /*0x3b69*/
      && (!(*(_DWORD *)v61 ^ 0x6E6E6F63 | *(_DWORD *)(v61 + 3) ^ 0x7463656E)
       || !(*(_DWORD *)v61 ^ 0x74736572 | *(_DWORD *)(v61 + 3) ^ 0x74726174)) )
    {
      goto LABEL_27; /*0x3b6b*/
    }
    if ( v60[1] == 10 ) /*0x3afa*/
    {
      if ( !(*(_QWORD *)v61 ^ 0x656E6E6F63736964LL | *((unsigned __int16 *)v61 + 4) ^ 0x7463LL) ) /*0x3b1a*/
        goto LABEL_20; /*0x3b1a*/
      v4 = v60[1]; /*0x3b1c*/
    }
    if ( v4 != 4 || *(_DWORD *)v61 != 1953719668 ) /*0x3b34*/
      goto LABEL_26; /*0x3b34*/
LABEL_29:
    v9 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, "command: ", 9);
    if ( (v60[0] & 1) != 0 ) /*0x3c35*/
    {
      v10 = v61; /*0x3c3b*/
      v11 = v60[1]; /*0x3c3f*/
    }
    else
    {
      v11 = LOBYTE(v60[0]) >> 1; /*0x3ead*/
      v10 = (char *)v60 + 1; /*0x3eaf*/
    }
    v25 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v9, v10, v11); /*0x3ebb*/
    std::ios_base::getloc((const std::ios_base *)v64); /*0x3ecf*/
    v26 = std::locale::use_facet((const std::locale *)v64, &std::ctype<char>::id); /*0x3ede*/
    v27 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v26->__vftable[2].~facet_0)(v26, 10); /*0x3ef1*/
    std::locale::~locale((std::locale *)v64); /*0x3ef7*/
    v21 = (unsigned int)v27; /*0x3efc*/
    std::ostream::put(v25, v21); /*0x3f03*/
    std::ostream::flush(v25); /*0x3f0b*/
    v23 = *(_QWORD *)(a1 + 8); /*0x3f15*/
    if ( *(_QWORD *)(a1 + 32) >= 2u ) /*0x3f19*/
    {
      v24 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 8LL); /*0x3f23*/
      *(_QWORD *)&v59 = *(_QWORD *)(a1 + 8); /*0x3f27*/
      goto LABEL_75; /*0x3f2b*/
    }
    goto LABEL_74; /*0x3f19*/
  }
  v3 = v60[0] & 0xFE; /*0x3a9f*/
  if ( v3 == 8 ) /*0x3aa5*/
  {
    if ( *(_DWORD *)((char *)v60 + 1) != 1953719668 ) /*0x3bd2*/
    {
LABEL_26:
      LOBYTE(v64[0]) = 28; /*0x3bd4*/
      strcpy((char *)v64 + 1, "Err command!!!"); /*0x3be6*/
      goto LABEL_90; /*0x3bfc*/
    }
    goto LABEL_29; /*0x3bd2*/
  }
  if ( v3 == 14 ) /*0x3aae*/
  {
    if ( *(_DWORD *)((char *)v60 + 1) ^ 0x6E6E6F63 | HIDWORD(v60[0]) ^ 0x7463656E /*0x3bb2*/
      && *(_DWORD *)((char *)v60 + 1) ^ 0x74736572 | HIDWORD(v60[0]) ^ 0x74726174 )
    {
      goto LABEL_26; /*0x3bb4*/
    }
LABEL_27:
    v7 = *(_QWORD *)(a1 + 8); /*0x3c01*/
    if ( *(_QWORD *)(a1 + 32) < 2u ) /*0x3c0a*/
    {
      *(_QWORD *)&v64[0] = *(_QWORD *)(a1 + 8); /*0x3c48*/
      v7 = Napi::Env::Undefined((Napi::Env *)v64); /*0x3c50*/
    }
    else
    {
      v8 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 8LL); /*0x3c10*/
    }
    v62 = v7; /*0x3c55*/
    v63 = v8; /*0x3c59*/
    Napi::String::Utf8Value((Napi::String *)v64); /*0x3c65*/
    __p[0] = *(void **)&v64[1]; /*0x3c83*/
    *(_OWORD *)__sz = v64[0]; /*0x3c8e*/
    v12 = *(_QWORD *)(a1 + 8); /*0x3c9a*/
    if ( *(_QWORD *)(a1 + 32) < 3u ) /*0x3c9e*/
    {
      *(_QWORD *)&v64[0] = *(_QWORD *)(a1 + 8); /*0x3caa*/
      v12 = Napi::Env::Undefined((Napi::Env *)v64); /*0x3cb2*/
    }
    else
    {
      v13 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 16LL); /*0x3ca4*/
    }
    v62 = v12; /*0x3cb7*/
    v63 = v13; /*0x3cbb*/
    Napi::String::Utf8Value((Napi::String *)v64); /*0x3cc7*/
    if ( ((__int64)__p[1] & 1) != 0 ) /*0x3cda*/
      operator delete(__p[3]); /*0x3ce3*/
    __p[3] = *(void **)&v64[1]; /*0x3cec*/
    *(_OWORD *)&__p[1] = v64[0]; /*0x3cf4*/
    v14 = *(_QWORD *)(a1 + 8); /*0x3cfd*/
    if ( *(_QWORD *)(a1 + 32) < 4u ) /*0x3d01*/
    {
      *(_QWORD *)&v64[0] = *(_QWORD *)(a1 + 8); /*0x3d0d*/
      v14 = Napi::Env::Undefined((Napi::Env *)v64); /*0x3d15*/
    }
    else
    {
      v15 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 24LL); /*0x3d07*/
    }
    v62 = v14; /*0x3d1a*/
    v63 = v15; /*0x3d1e*/
    Napi::String::Utf8Value((Napi::String *)v64); /*0x3d2a*/
    if ( (v53[0] & 1) != 0 ) /*0x3d3d*/
      operator delete(__s[0]); /*0x3d46*/
    __s[0] = *(char **)&v64[1]; /*0x3d4f*/
    *(_OWORD *)v53 = v64[0]; /*0x3d57*/
    v16 = *(_QWORD *)(a1 + 8); /*0x3d60*/
    if ( *(_QWORD *)(a1 + 32) < 5u ) /*0x3d64*/
    {
      *(_QWORD *)&v64[0] = *(_QWORD *)(a1 + 8); /*0x3d70*/
      v16 = Napi::Env::Undefined((Napi::Env *)v64); /*0x3d78*/
    }
    else
    {
      v17 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 32LL); /*0x3d6a*/
    }
    v62 = v16; /*0x3d7d*/
    v63 = v17; /*0x3d81*/
    Napi::String::Utf8Value((Napi::String *)v64); /*0x3d8d*/
    if ( ((__int64)__s[1] & 1) != 0 ) /*0x3da0*/
      operator delete(__s[3]); /*0x3da9*/
    __s[3] = *(char **)&v64[1]; /*0x3db2*/
    *(_OWORD *)&__s[1] = v64[0]; /*0x3dba*/
    *(_QWORD *)&v18 = *(_QWORD *)(a1 + 8); /*0x3dc3*/
    if ( *(_QWORD *)(a1 + 32) < 6u ) /*0x3dc7*/
    {
      *(_QWORD *)&v64[0] = *(_QWORD *)(a1 + 8); /*0x3dd3*/
      *(_QWORD *)&v18 = Napi::Env::Undefined((Napi::Env *)v64); /*0x3ddb*/
    }
    else
    {
      *((_QWORD *)&v18 + 1) = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 40LL); /*0x3dcd*/
    }
    v64[0] = v18; /*0x3de0*/
    v55 = Napi::Number::Int32Value((Napi::Number *)v64); /*0x3df1*/
    v19 = *(_QWORD *)(a1 + 8); /*0x3dfc*/
    if ( *(_QWORD *)(a1 + 32) < 7u ) /*0x3e00*/
    {
      *(_QWORD *)&v64[0] = *(_QWORD *)(a1 + 8); /*0x3e0c*/
      v19 = Napi::Env::Undefined((Napi::Env *)v64); /*0x3e14*/
    }
    else
    {
      v20 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 48LL); /*0x3e06*/
    }
    v62 = v19; /*0x3e19*/
    v63 = v20; /*0x3e1d*/
    v21 = (unsigned __int64)&v62; /*0x3e25*/
    Napi::String::Utf8Value((Napi::String *)v64); /*0x3e29*/
    if ( (v56[0] & 1) != 0 ) /*0x3e35*/
      operator delete(v57); /*0x3e3e*/
    v57 = *(std::string::value_type **)&v64[1]; /*0x3e47*/
    *(_OWORD *)v56 = v64[0]; /*0x3e4f*/
    *(_QWORD *)&v22 = *(_QWORD *)(a1 + 8); /*0x3e59*/
    if ( *(_QWORD *)(a1 + 32) < 8u ) /*0x3e5d*/
    {
      *(_QWORD *)&v64[0] = *(_QWORD *)(a1 + 8); /*0x3e69*/
      *(_QWORD *)&v22 = Napi::Env::Undefined((Napi::Env *)v64); /*0x3e71*/
    }
    else
    {
      *((_QWORD *)&v22 + 1) = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 56LL); /*0x3e63*/
    }
    v64[0] = v22; /*0x3e76*/
    v58 = Napi::Number::Int32Value((Napi::Number *)v64); /*0x3e87*/
    v23 = *(_QWORD *)(a1 + 8); /*0x3e92*/
    if ( *(_QWORD *)(a1 + 32) >= 9u ) /*0x3e96*/
    {
      v24 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 64LL); /*0x3ea0*/
      *(_QWORD *)&v59 = *(_QWORD *)(a1 + 8); /*0x3ea4*/
      goto LABEL_75; /*0x3ea8*/
    }
    goto LABEL_74; /*0x3e96*/
  }
  if ( v3 != 20 /*0x3ad6*/
    || *(std::string::size_type *)((char *)v60 + 1) ^ 0x656E6E6F63736964LL
     | *(unsigned __int16 *)((char *)&v60[1] + 1) ^ 0x7463LL )
  {
    goto LABEL_26; /*0x3ad9*/
  }
LABEL_20:
  v5 = *(_QWORD *)(a1 + 8); /*0x3b72*/
  if ( *(_QWORD *)(a1 + 32) < 2u ) /*0x3b7b*/
  {
    *(_QWORD *)&v64[0] = *(_QWORD *)(a1 + 8); /*0x3f30*/
    v5 = Napi::Env::Undefined((Napi::Env *)v64); /*0x3f38*/
  }
  else
  {
    v6 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 8LL); /*0x3b85*/
  }
  v62 = v5; /*0x3f3d*/
  v63 = v6; /*0x3f41*/
  Napi::String::Utf8Value((Napi::String *)v64); /*0x3f4d*/
  if ( (v53[0] & 1) != 0 ) /*0x3f60*/
    operator delete(__s[0]); /*0x3f69*/
  __s[0] = *(char **)&v64[1]; /*0x3f72*/
  *(_OWORD *)v53 = v64[0]; /*0x3f7a*/
  v28 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, "command: ", 9);
  if ( (v60[0] & 1) != 0 ) /*0x3fa0*/
  {
    v29 = v61; /*0x3fa2*/
    v30 = v60[1]; /*0x3fa6*/
  }
  else
  {
    v30 = LOBYTE(v60[0]) >> 1; /*0x3fac*/
    v29 = (char *)v60 + 1; /*0x3fae*/
  }
  v31 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v28, v29, v30); /*0x3fba*/
  std::ios_base::getloc((const std::ios_base *)v64); /*0x3fce*/
  v32 = std::locale::use_facet((const std::locale *)v64, &std::ctype<char>::id); /*0x3fdd*/
  v33 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v32->__vftable[2].~facet_0)(v32, 10); /*0x3ff0*/
  std::locale::~locale((std::locale *)v64); /*0x3ff6*/
  std::ostream::put(v31, (unsigned int)v33); /*0x4002*/
  std::ostream::flush(v31); /*0x400a*/
  v34 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, " vmID: ", 7);
  if ( (v53[0] & 1) != 0 ) /*0x402d*/
    v35 = __s[0]; /*0x402f*/
  else
    v35 = (char *)v53 + 1; /*0x4038*/
  v36 = strlen(v35); /*0x4050*/
  v37 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v34, v35, v36); /*0x4063*/
  std::ios_base::getloc((const std::ios_base *)v64); /*0x4077*/
  v38 = std::locale::use_facet((const std::locale *)v64, &std::ctype<char>::id); /*0x4082*/
  v39 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v38->__vftable[2].~facet_0)(v38, 10); /*0x4095*/
  std::locale::~locale((std::locale *)v64); /*0x409b*/
  v21 = (unsigned int)v39; /*0x40a0*/
  std::ostream::put(v37, v21); /*0x40a7*/
  std::ostream::flush(v37); /*0x40af*/
  v23 = *(_QWORD *)(a1 + 8); /*0x40b9*/
  if ( *(_QWORD *)(a1 + 32) >= 3u ) /*0x40bd*/
  {
    v24 = *(_QWORD *)(*(_QWORD *)(a1 + 40) + 16LL); /*0x40c3*/
    *(_QWORD *)&v59 = *(_QWORD *)(a1 + 8); /*0x40c7*/
    goto LABEL_75; /*0x40cb*/
  }
LABEL_74:
  *(_QWORD *)&v64[0] = v23; /*0x40cd*/
  v23 = Napi::Env::Undefined((Napi::Env *)v64); /*0x40da*/
  *(_QWORD *)&v59 = v23; /*0x40dd*/
LABEL_75:
  *((_QWORD *)&v59 + 1) = v24; /*0x40e1*/
  v40 = (char *)operator new(0x108u); /*0x40ef*/
  v62 = Napi::Object::New(v23, v21); /*0x40fa*/
  v63 = v41; /*0x40fe*/
  *(_QWORD *)&v64[0] = Napi::Object::New(v59, v21); /*0x410b*/
  *((_QWORD *)&v64[0] + 1) = v42; /*0x410f*/
  Napi::AsyncWorker::AsyncWorker(v40, v64, &v59, "generic", &v62); /*0x4129*/
  *(_QWORD *)v40 = off_8378; /*0x4135*/
  v43 = (std::string *)(v40 + 104); /*0x4138*/
  if ( (v60[0] & 1) != 0 ) /*0x4140*/
  {
    std::string::__init_copy_ctor_external(v43, v61, v60[1]); /*0x41fe*/
    v44 = (std::string *)(v40 + 128); /*0x4203*/
    if ( (__sz[0] & 1) != 0 ) /*0x4211*/
    {
LABEL_77:
      std::string::__init_copy_ctor_external(v44, (const std::string::value_type *)__p[0], __sz[1]); /*0x4169*/
      v45 = (std::string *)(v40 + 152); /*0x417c*/
      if ( ((__int64)__p[1] & 1) != 0 ) /*0x418a*/
        goto LABEL_78; /*0x418a*/
      goto LABEL_83; /*0x418a*/
    }
  }
  else
  {
    *((_QWORD *)v40 + 15) = v61; /*0x414a*/
    *(_OWORD *)&v43->__r_.__value_.__l.0 = *(_OWORD *)v60; /*0x4152*/
    v44 = (std::string *)(v40 + 128); /*0x4155*/
    if ( (__sz[0] & 1) != 0 ) /*0x4163*/
      goto LABEL_77; /*0x4163*/
  }
  v44->__r_.__value_.__l.__data_ = (std::string::pointer)__p[0]; /*0x421e*/
  *(_OWORD *)&v44->__r_.__value_.__l.0 = *(_OWORD *)__sz; /*0x4229*/
  v45 = (std::string *)(v40 + 152); /*0x422c*/
  if ( ((__int64)__p[1] & 1) != 0 ) /*0x423a*/
  {
LABEL_78:
    std::string::__init_copy_ctor_external(v45, (const std::string::value_type *)__p[3], (std::string::size_type)__p[2]); /*0x4190*/
    v46 = (std::string *)(v40 + 176); /*0x41a3*/
    if ( (v53[0] & 1) != 0 ) /*0x41b1*/
      goto LABEL_79; /*0x41b1*/
LABEL_84:
    v46->__r_.__value_.__l.__data_ = __s[0]; /*0x4269*/
    *(_OWORD *)&v46->__r_.__value_.__l.0 = *(_OWORD *)v53; /*0x427b*/
    v47 = (std::string *)(v40 + 200); /*0x427e*/
    if ( ((__int64)__s[1] & 1) != 0 ) /*0x428c*/
      goto LABEL_80; /*0x428c*/
LABEL_85:
    v47->__r_.__value_.__l.__data_ = __s[3]; /*0x4292*/
    *(_OWORD *)&v47->__r_.__value_.__l.0 = *(_OWORD *)&__s[1]; /*0x42a4*/
    goto LABEL_86; /*0x42a4*/
  }
LABEL_83:
  v45->__r_.__value_.__l.__data_ = (std::string::pointer)__p[3]; /*0x4240*/
  *(_OWORD *)&v45->__r_.__value_.__l.0 = *(_OWORD *)&__p[1]; /*0x4252*/
  v46 = (std::string *)(v40 + 176); /*0x4255*/
  if ( (v53[0] & 1) == 0 ) /*0x4263*/
    goto LABEL_84; /*0x4263*/
LABEL_79:
  std::string::__init_copy_ctor_external(v46, __s[0], v53[1]); /*0x41b7*/
  v47 = (std::string *)(v40 + 200); /*0x41ca*/
  if ( ((__int64)__s[1] & 1) == 0 ) /*0x41d8*/
    goto LABEL_85; /*0x41d8*/
LABEL_80:
  std::string::__init_copy_ctor_external(v47, __s[3], (std::string::size_type)__s[2]); /*0x41de*/
LABEL_86:
  *((_DWORD *)v40 + 56) = v55; /*0x42a7*/
  v48 = (std::string *)(v40 + 232); /*0x42b7*/
  if ( (v56[0] & 1) != 0 ) /*0x42c5*/
  {
    std::string::__init_copy_ctor_external(v48, v57, v56[1]); /*0x42e7*/
  }
  else
  {
    *((_QWORD *)v40 + 31) = v57; /*0x42cb*/
    *(_OWORD *)&v48->__r_.__value_.__l.0 = *(_OWORD *)v56; /*0x42d4*/
  }
  *((_DWORD *)v40 + 64) = v58; /*0x42f2*/
  Napi::AsyncWorker::Queue((Napi::AsyncWorker *)v40); /*0x42fc*/
  strcpy((char *)v64, "*Commond run finished!"); /*0x4301*/
LABEL_90:
  v49 = Napi::String::New(*(_QWORD *)(a1 + 8), (char *)v64 + 1); /*0x4326*/
  if ( (v64[0] & 1) != 0 ) /*0x4339*/
  {
    operator delete(*(void **)&v64[1]); /*0x439e*/
    if ( (v60[0] & 1) == 0 ) /*0x43a7*/
    {
LABEL_92:
      if ( (v56[0] & 1) == 0 ) /*0x4348*/
        goto LABEL_93; /*0x4348*/
      goto LABEL_101; /*0x4348*/
    }
  }
  else if ( (v60[0] & 1) == 0 ) /*0x433f*/
  {
    goto LABEL_92; /*0x433f*/
  }
  operator delete(v61); /*0x43ad*/
  if ( (v56[0] & 1) == 0 ) /*0x43b9*/
  {
LABEL_93:
    if ( ((__int64)__s[1] & 1) == 0 ) /*0x4351*/
      goto LABEL_94; /*0x4351*/
    goto LABEL_102; /*0x4351*/
  }
LABEL_101:
  operator delete(v57); /*0x43bb*/
  if ( ((__int64)__s[1] & 1) == 0 ) /*0x43ce*/
  {
LABEL_94:
    if ( (v53[0] & 1) == 0 ) /*0x435a*/
      goto LABEL_95; /*0x435a*/
    goto LABEL_103; /*0x435a*/
  }
LABEL_102:
  operator delete(__s[3]); /*0x43d0*/
  if ( (v53[0] & 1) == 0 ) /*0x43e3*/
  {
LABEL_95:
    if ( ((__int64)__p[1] & 1) == 0 ) /*0x4367*/
      goto LABEL_96; /*0x4367*/
LABEL_104:
    operator delete(__p[3]); /*0x4402*/
    if ( (__sz[0] & 1) == 0 ) /*0x4415*/
      return v49; /*0x4415*/
    goto LABEL_97; /*0x4415*/
  }
LABEL_103:
  operator delete(__s[0]); /*0x43e9*/
  if ( ((__int64)__p[1] & 1) != 0 ) /*0x43fc*/
    goto LABEL_104; /*0x43fc*/
LABEL_96:
  if ( (__sz[0] & 1) != 0 ) /*0x4374*/
LABEL_97:
    operator delete(__p[0]); /*0x4376*/
  return v49; /*0x4388*/
}
