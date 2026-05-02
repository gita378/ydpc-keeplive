// 0x4def0 @ 0x4def0
__int64 __fastcall ClientManager::SohoSdk_StartConnectDesktop(
        ClientManager *a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        __int64 a5,
        __int64 a6,
        char a7)
{
  unsigned __int64 v8; // rcx
  char v9; // dl
  std::string::size_type size; // rax
  std::string::size_type v11; // rsi
  __int64 v12; // rdi
  ClientManager *v13; // rsi
  void *v14; // rdi
  std::string::pointer data; // rdx
  ClientManager *v16; // rax
  __int64 CurrentMSecsSinceEpoch; // rax
  ClientManager *v18; // rcx
  _OWORD *v19; // rdi
  size_t v20; // rax
  size_t v21; // r15
  char *v22; // r14
  size_t v23; // rbx
  ClientManager *v24; // rdi
  ClientManager *v25; // rax
  const char *v26; // r12
  __int64 v27; // rcx
  unsigned int v28; // ebx
  size_t v29; // rax
  size_t v30; // r15
  char *v31; // r13
  size_t v32; // r14
  __int64 v33; // rbx
  char *v34; // rdx
  unsigned __int64 v35; // rcx
  size_t v36; // rax
  size_t v37; // r15
  __int64 v38; // r12
  char *v39; // r14
  size_t v40; // rbx
  char *v41; // rdx
  unsigned __int64 v42; // rcx
  size_t v43; // rax
  size_t v44; // r15
  char *v45; // r14
  size_t v46; // rbx
  char *v47; // rdx
  unsigned __int64 v48; // rcx
  char *v49; // r13
  __int64 v50; // r14
  char *v51; // r15
  char *v52; // rbx
  size_t v53; // rbx
  unsigned __int64 v54; // rax
  size_t v55; // r13
  _BYTE *v56; // r14
  int v57; // r12d
  __int64 v58; // rbx
  __int64 v59; // rax
  int v60; // eax
  ClientManager *v61; // rdi
  void **v62; // r14
  void **v63; // rbx
  void *v64; // rdi
  void **v65; // r15
  _WORD v67[8]; // [rsp+10h] [rbp-2E90h] BYREF
  void *v68; // [rsp+20h] [rbp-2E80h]
  __int16 v69; // [rsp+28h] [rbp-2E78h] BYREF
  unsigned __int64 v70; // [rsp+30h] [rbp-2E70h]
  void *v71; // [rsp+38h] [rbp-2E68h]
  _QWORD __dst[2]; // [rsp+40h] [rbp-2E60h] BYREF
  void *v73; // [rsp+50h] [rbp-2E50h]
  _QWORD v74[2]; // [rsp+58h] [rbp-2E48h] BYREF
  void *__p; // [rsp+68h] [rbp-2E38h]
  __int128 v76; // [rsp+70h] [rbp-2E30h] BYREF
  void *v77; // [rsp+80h] [rbp-2E20h]
  __int128 v78; // [rsp+90h] [rbp-2E10h] BYREF
  void *v79; // [rsp+A0h] [rbp-2E00h]
  std::string v80; // [rsp+A8h] [rbp-2DF8h] BYREF
  void *v81[2]; // [rsp+C0h] [rbp-2DE0h] BYREF
  char *v82; // [rsp+D0h] [rbp-2DD0h]
  __int64 v83; // [rsp+E0h] [rbp-2DC0h]
  unsigned int v84; // [rsp+ECh] [rbp-2DB4h]
  __int64 v85; // [rsp+F0h] [rbp-2DB0h] BYREF
  size_t __sz; // [rsp+F8h] [rbp-2DA8h]
  void *__src; // [rsp+100h] [rbp-2DA0h]
  ClientManager *v88; // [rsp+108h] [rbp-2D98h]
  _OWORD v89[5]; // [rsp+110h] [rbp-2D90h] BYREF
  char v90[792]; // [rsp+160h] [rbp-2D40h] BYREF
  __int128 v91; // [rsp+478h] [rbp-2A28h]
  __int128 v92; // [rsp+488h] [rbp-2A18h]
  __int128 v93; // [rsp+498h] [rbp-2A08h]
  __int128 v94; // [rsp+4A8h] [rbp-29F8h]
  __int128 v95; // [rsp+4B8h] [rbp-29E8h]
  __int128 v96; // [rsp+4C8h] [rbp-29D8h]
  __int128 v97; // [rsp+4D8h] [rbp-29C8h]
  _BYTE v98[29]; // [rsp+4E8h] [rbp-29B8h] BYREF
  _BYTE v99[284]; // [rsp+508h] [rbp-2998h] BYREF
  char v100[272]; // [rsp+624h] [rbp-287Ch] BYREF
  char v101[1588]; // [rsp+734h] [rbp-276Ch] BYREF
  char v102[264]; // [rsp+D68h] [rbp-2138h] BYREF
  char v103[6432]; // [rsp+E70h] [rbp-2030h] BYREF
  void *v104; // [rsp+2790h] [rbp-710h]
  void **v105; // [rsp+2798h] [rbp-708h]
  __int128 v106; // [rsp+2E3Ch] [rbp-64h]
  void *v107[2]; // [rsp+2E4Ch] [rbp-54h]
  _BYTE v108[20]; // [rsp+2E5Ch] [rbp-44h] BYREF

  v88 = a1; /*0x4df07*/
  v84 = 0; /*0x4df1c*/
  memset(v89, 0, 78); /*0x4df68*/
  __bzero(v90, 791); /*0x4df74*/
  memset(v98, 0, sizeof(v98)); /*0x4df83*/
  v97 = 0; /*0x4df8a*/
  v96 = 0; /*0x4df91*/
  v95 = 0; /*0x4df98*/
  v94 = 0; /*0x4df9f*/
  v93 = 0; /*0x4dfa6*/
  v92 = 0; /*0x4dfad*/
  v91 = 0; /*0x4dfb4*/
  __bzero(v99, 265); /*0x4dfc3*/
  memset(&v99[268], 0, 13); /*0x4dfd3*/
  __bzero(v100, 269); /*0x4dfe6*/
  __bzero(v101, 1586); /*0x4dff3*/
  __bzero(v102, 261); /*0x4e000*/
  __bzero(v103, 8139); /*0x4e011*/
  memset(v108, 0, sizeof(v108)); /*0x4e019*/
  *(_OWORD *)v107 = 0; /*0x4e01d*/
  v106 = 0; /*0x4e021*/
  GetLanguageType(); /*0x4e033*/
  v8 = (unsigned __int64)*(_BYTE *)&v80.__r_.__value_.__l.0 >> 1; /*0x4e042*/
  v9 = *(_BYTE *)&v80.__r_.__value_.__s.0 & 1; /*0x4e045*/
  size = v80.__r_.__value_.__l.__size_; /*0x4e048*/
  v11 = v80.__r_.__value_.__l.__size_; /*0x4e04f*/
  if ( (*(_BYTE *)&v80.__r_.__value_.__s.0 & 1) == 0 ) /*0x4e052*/
    v11 = (unsigned __int64)*(_BYTE *)&v80.__r_.__value_.__l.0 >> 1; /*0x4e052*/
  if ( !v11 ) /*0x4e059*/
  {
    std::string::assign(&v80, "zh"); /*0x4e069*/
    size = v80.__r_.__value_.__l.__size_; /*0x4e075*/
    v9 = *(_BYTE *)&v80.__r_.__value_.__s.0 & 1; /*0x4e07e*/
    v8 = (unsigned __int64)*(_BYTE *)&v80.__r_.__value_.__l.0 >> 1; /*0x4e081*/
  }
  v12 = *(_QWORD *)(a2 + 3608); /*0x4e084*/
  v13 = v88; /*0x4e08c*/
  *((_QWORD *)v88 + 2944) = v12; /*0x4e093*/
  *((_QWORD *)v13 + 495) = v12; /*0x4e09a*/
  v14 = (void *)(v12 + 5283); /*0x4e0a1*/
  if ( v9 ) /*0x4e0aa*/
  {
    data = v80.__r_.__value_.__l.__data_; /*0x4e0ac*/
    v8 = size; /*0x4e0b3*/
  }
  else
  {
    data = v80.__r_.__value_.__s.__data_; /*0x4e0b8*/
  }
  ZXMemcpy(v14, 0x15u, data, v8); /*0x4e0c4*/
  v16 = v88; /*0x4e0c9*/
  *((_DWORD *)v88 + 2336) = 2; /*0x4e0d0*/
  *((_DWORD *)v16 + 5741) = 1; /*0x4e0da*/
  CurrentMSecsSinceEpoch = GetCurrentMSecsSinceEpoch(); /*0x4e0e4*/
  v18 = v88; /*0x4e0ed*/
  *((_QWORD *)v88 + 758) = CurrentMSecsSinceEpoch; /*0x4e0f4*/
  *((_DWORD *)v18 + 5886) = 1; /*0x4e0fb*/
  *(_DWORD *)(a2 + 22336) = 1; /*0x4e105*/
  v19 = *(_OWORD **)(a2 + 3616); /*0x4e111*/
  if ( !v19 ) /*0x4e11c*/
  {
    v19 = v89; /*0x4e11e*/
    *(_QWORD *)(a2 + 3616) = v89; /*0x4e125*/
  }
  ZXMemcpy((char *)v19 + 4, 0x25u, &STACK[0x38B7], 0x25u); /*0x4e145*/
  *(_BYTE *)(*(_QWORD *)(a2 + 3616) + 40LL) = 0; /*0x4e152*/
  v69 = 0; /*0x4e156*/
  v20 = strlen((const char *)&STACK[0x32B5]); /*0x4e169*/
  if ( v20 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x4e172*/
    std::string::__throw_length_error[abi:v15006](__dst); /*0x4ea0f*/
  v21 = v20; /*0x4e178*/
  v83 = a2; /*0x4e186*/
  if ( v20 >= 0x17 ) /*0x4e18d*/
  {
    v23 = (v20 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x4e1ae*/
    v22 = (char *)operator new(v23); /*0x4e1ba*/
    v73 = v22; /*0x4e1bd*/
    __dst[0] = v23 | 1; /*0x4e1c8*/
    __dst[1] = v21; /*0x4e1cf*/
    goto LABEL_15; /*0x4e1cf*/
  }
  LOBYTE(__dst[0]) = 2 * v20; /*0x4e193*/
  v22 = (char *)__dst + 1; /*0x4e199*/
  if ( v20 ) /*0x4e1a3*/
LABEL_15:
    memcpy(v22, &STACK[0x32B5], v21); /*0x4e1d6*/
  v22[v21] = 0; /*0x4e1e4*/
  UrlEncode(__dst, &v69); /*0x4e1fe*/
  v24 = v88; /*0x4e203*/
  *(_DWORD *)(*((_QWORD *)v88 + 2944) + 6856LL) = 10; /*0x4e211*/
  ClientManager::UpdateReqSerialNum(v24); /*0x4e21b*/
  v25 = v88; /*0x4e220*/
  *((_DWORD *)v88 + 988) = 2; /*0x4e227*/
  v26 = (const char *)(v83 + 5720); /*0x4e238*/
  ZXMemcpy((void *)(v83 + 5720), 0x25u, (char *)v25 + 6072, 0x25u); /*0x4e253*/
  v27 = v83; /*0x4e265*/
  *(_DWORD *)(v83 + 3600) = *((_DWORD *)v88 + 988); /*0x4e26c*/
  *(_DWORD *)(v27 + 3604) = -1; /*0x4e272*/
  v28 = v84; /*0x4e27c*/
  v29 = strlen(v26); /*0x4e285*/
  if ( v29 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x4e28e*/
    std::string::__throw_length_error[abi:v15006](v74); /*0x4ea1d*/
  v30 = v29; /*0x4e294*/
  if ( v29 >= 0x17 ) /*0x4e29b*/
  {
    v32 = (v29 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x4e2bc*/
    v31 = (char *)operator new(v32); /*0x4e2c8*/
    __p = v31; /*0x4e2cb*/
    v74[0] = v32 | 1; /*0x4e2d6*/
    v74[1] = v30; /*0x4e2dd*/
    goto LABEL_21; /*0x4e2dd*/
  }
  LOBYTE(v74[0]) = 2 * v29; /*0x4e2a1*/
  v31 = (char *)v74 + 1; /*0x4e2a7*/
  if ( v29 ) /*0x4e2b1*/
LABEL_21:
    memcpy(v31, v26, v30); /*0x4e2e4*/
  v31[v30] = 0; /*0x4e2f2*/
  CTraceManager::setVdnumKey(v28, v74); /*0x4e301*/
  v33 = v83; /*0x4e30d*/
  if ( (v74[0] & 1) != 0 ) /*0x4e314*/
    operator delete(__p); /*0x4e31d*/
  if ( (v69 & 1) != 0 ) /*0x4e338*/
  {
    v34 = (char *)v71; /*0x4e33a*/
    v35 = v70; /*0x4e341*/
  }
  else
  {
    v34 = (char *)&v69 + 1; /*0x4e34a*/
    v35 = (unsigned __int64)(unsigned __int8)v69 >> 1; /*0x4e351*/
  }
  ZXMemcpy((void *)(*(_QWORD *)(v33 + 3608) + 517LL), 0x200u, v34, v35); /*0x4e359*/
  ZXMemcpy((void *)(*(_QWORD *)(v83 + 3608) + 4LL), 0x200u, &STACK[0x32B5], 0x200u); /*0x4e381*/
  v76 = 0; /*0x4e389*/
  v77 = 0; /*0x4e390*/
  v36 = strlen((const char *)&STACK[0x34B6]); /*0x4e3a9*/
  if ( v36 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x4e3b2*/
    std::string::__throw_length_error[abi:v15006](&v85); /*0x4ea2b*/
  v37 = v36; /*0x4e3b8*/
  v38 = v83; /*0x4e3bf*/
  if ( v36 >= 0x17 ) /*0x4e3c6*/
  {
    v40 = (v36 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x4e3e7*/
    v39 = (char *)operator new(v40); /*0x4e3f3*/
    __src = v39; /*0x4e3f6*/
    v85 = v40 | 1; /*0x4e401*/
    __sz = v37; /*0x4e408*/
    goto LABEL_32; /*0x4e408*/
  }
  LOBYTE(v85) = 2 * v36; /*0x4e3cc*/
  v39 = (char *)&v85 + 1; /*0x4e3d2*/
  if ( v36 ) /*0x4e3dc*/
LABEL_32:
    memcpy(v39, &STACK[0x34B6], v37); /*0x4e40f*/
  v39[v37] = 0; /*0x4e41d*/
  AesCbcEncode(&v85, &v76); /*0x4e430*/
  if ( (v85 & 1) != 0 ) /*0x4e43c*/
    operator delete(__src); /*0x4e445*/
  if ( (v76 & 1) != 0 ) /*0x4e461*/
  {
    v41 = (char *)v77; /*0x4e463*/
    v42 = *((_QWORD *)&v76 + 1); /*0x4e46a*/
  }
  else
  {
    v42 = (unsigned __int64)(unsigned __int8)v76 >> 1; /*0x4e473*/
    v41 = (char *)&v76 + 1; /*0x4e476*/
  }
  ZXMemcpy((void *)(*(_QWORD *)(v38 + 3608) + 1030LL), 0x400u, v41, v42); /*0x4e482*/
  *(_BYTE *)(*(_QWORD *)(v38 + 3608) + 2054LL) = 0; /*0x4e48f*/
  v43 = strlen((const char *)&STACK[0x34B6]); /*0x4e499*/
  if ( v43 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x4e4a2*/
    std::string::__throw_length_error[abi:v15006](&v85); /*0x4ea39*/
  v44 = v43; /*0x4e4a8*/
  if ( v43 >= 0x17 ) /*0x4e4af*/
  {
    v46 = (v43 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x4e4d0*/
    v45 = (char *)operator new(v46); /*0x4e4dc*/
    __src = v45; /*0x4e4df*/
    v85 = v46 | 1; /*0x4e4ea*/
    __sz = v44; /*0x4e4f1*/
    goto LABEL_43; /*0x4e4f1*/
  }
  LOBYTE(v85) = 2 * v43; /*0x4e4b5*/
  v45 = (char *)&v85 + 1; /*0x4e4bb*/
  if ( v43 ) /*0x4e4c5*/
LABEL_43:
    memcpy(v45, &STACK[0x34B6], v44); /*0x4e4f8*/
  v45[v44] = 0; /*0x4e506*/
  v67[0] = 0; /*0x4e50b*/
  UrlEncode(&v85, v67); /*0x4e522*/
  v78 = 0; /*0x4e52a*/
  v79 = 0; /*0x4e531*/
  AesCbcEncode(v67, &v78); /*0x4e54a*/
  if ( (v78 & 1) != 0 ) /*0x4e566*/
  {
    v47 = (char *)v79; /*0x4e568*/
    v48 = *((_QWORD *)&v78 + 1); /*0x4e56f*/
  }
  else
  {
    v48 = (unsigned __int64)(unsigned __int8)v78 >> 1; /*0x4e578*/
    v47 = (char *)&v78 + 1; /*0x4e57b*/
  }
  ZXMemcpy((void *)(*(_QWORD *)(v38 + 3608) + 2055LL), 0x400u, v47, v48); /*0x4e587*/
  if ( (v85 & 1) != 0 ) /*0x4e598*/
  {
    v49 = (char *)__src; /*0x4e59a*/
    v50 = __sz; /*0x4e5a1*/
  }
  else
  {
    v49 = (char *)&v85 + 1; /*0x4e5aa*/
    v50 = (unsigned __int64)(unsigned __int8)v85 >> 1; /*0x4e5b1*/
  }
  *(_OWORD *)v81 = 0; /*0x4e5b7*/
  v82 = 0; /*0x4e5be*/
  if ( v50 ) /*0x4e5cc*/
  {
    if ( v50 < 0 ) /*0x4e5ce*/
      std::vector<char>::__throw_length_error[abi:v15006](v81); /*0x4ea5a*/
    v51 = (char *)operator new(v50); /*0x4e5dc*/
    v81[0] = v51; /*0x4e5df*/
    v81[1] = v51; /*0x4e5e6*/
    v52 = &v51[v50]; /*0x4e5f0*/
    v82 = &v51[v50]; /*0x4e5f3*/
    memcpy(v51, v49, v50); /*0x4e603*/
    v81[1] = &v51[v50]; /*0x4e608*/
  }
  else
  {
    v51 = 0; /*0x4e611*/
    v52 = 0; /*0x4e614*/
  }
  v53 = v52 - v51; /*0x4e616*/
  v54 = v53 + 1; /*0x4e61c*/
  if ( (__int64)(v53 + 1) < 0 ) /*0x4e61f*/
    std::vector<char>::__throw_length_error[abi:v15006](v81); /*0x4ea47*/
  if ( 2 * v53 > v54 ) /*0x4e62c*/
    v54 = 2 * v53; /*0x4e62c*/
  v55 = 0x7FFFFFFFFFFFFFFFLL; /*0x4e63d*/
  if ( v53 < 0x3FFFFFFFFFFFFFFFLL ) /*0x4e647*/
    v55 = v54; /*0x4e647*/
  if ( v55 ) /*0x4e64e*/
    v56 = operator new(v55); /*0x4e658*/
  else
    v56 = 0; /*0x4e65d*/
  v56[v53] = 0; /*0x4e663*/
  v57 = (_DWORD)v56 + v53 + 1; /*0x4e66c*/
  memcpy(v56, v51, v53); /*0x4e678*/
  v81[0] = v56; /*0x4e67d*/
  v81[1] = &v56[v53 + 1]; /*0x4e684*/
  v82 = &v56[v55]; /*0x4e68b*/
  if ( v51 ) /*0x4e695*/
  {
    operator delete(v51); /*0x4e69a*/
    v56 = v81[0]; /*0x4e69f*/
    v57 = (int)v81[1]; /*0x4e6a6*/
  }
  v58 = v83; /*0x4e6ba*/
  AesEncodeForCsap(v56, (unsigned int)(v57 + ~(_DWORD)v56), *(_QWORD *)(v83 + 3608) + 3080LL, 1024, 1); /*0x4e6d6*/
  HideVecSensitiveInfo(v81); /*0x4e6e6*/
  v59 = *(_QWORD *)(v58 + 3608); /*0x4e6eb*/
  *(_DWORD *)(v59 + 6868) = 4; /*0x4e6f2*/
  *(_DWORD *)(v58 + 4680) = 4; /*0x4e6fc*/
  *(_BYTE *)(v59 + 4104) = 0; /*0x4e706*/
  memset_s((void *)(v58 + 1032), 0x1F5u, 0, 0x1F5u); /*0x4e723*/
  ZXMemcpy((void *)(v58 + 1032), 0x1F4u, &STACK[0x3AD8], 0x1F4u); /*0x4e73c*/
  *(_BYTE *)(v58 + 1532) = 0; /*0x4e741*/
  *(_DWORD *)(v58 + 1536) = STACK[0x3CD0]; /*0x4e74f*/
  ZXMemcpy((void *)(v58 + 12), 0x1F4u, &STACK[0x38DD], 0x1F4u); /*0x4e76a*/
  *(_BYTE *)(v58 + 512) = 0; /*0x4e76f*/
  v60 = STACK[0x3AD4]; /*0x4e776*/
  *(_DWORD *)(v58 + 1024) = STACK[0x3AD4]; /*0x4e77d*/
  *(_DWORD *)(v58 + 1020) = v60; /*0x4e783*/
  *(_DWORD *)(v58 + 1028) = 1; /*0x4e789*/
  *(_DWORD *)(v58 + 8) = 1; /*0x4e793*/
  v61 = v88; /*0x4e7a1*/
  if ( (unsigned __int8)ClientManager::GetSohoDesktopInfo(v88) ) /*0x4e7ab*/
  {
    if ( LODWORD(STACK[0x3CD4]) == 1 ) /*0x4e7bc*/
      ClientManager::SohoSdk_RestartSohoVd(v61, v58); /*0x4e7c1*/
    else
      ClientManager::GetSohoConnectStr(v88, v58, &a7, v84); /*0x4e805*/
  }
  else
  {
    write_log( /*0x4e7eb*/
      3,
      0,
      "SohoSdk_StartConnectDesktop",
      7745,
      "Vmid [%s] failed to get desktop info.",
      (const char *)&STACK[0x38B7]);
  }
  *(_QWORD *)(v58 + 3616) = 0; /*0x4e80a*/
  if ( v81[0] ) /*0x4e81f*/
  {
    v81[1] = v81[0]; /*0x4e821*/
    operator delete(v81[0]); /*0x4e828*/
  }
  if ( (v78 & 1) != 0 ) /*0x4e834*/
  {
    operator delete(v79); /*0x4e916*/
    if ( (v67[0] & 1) == 0 ) /*0x4e922*/
    {
LABEL_73:
      if ( (v85 & 1) == 0 ) /*0x4e84e*/
        goto LABEL_74; /*0x4e84e*/
      goto LABEL_93; /*0x4e84e*/
    }
  }
  else if ( (v67[0] & 1) == 0 ) /*0x4e841*/
  {
    goto LABEL_73; /*0x4e841*/
  }
  operator delete(v68); /*0x4e92f*/
  if ( (v85 & 1) == 0 ) /*0x4e93b*/
  {
LABEL_74:
    if ( (v76 & 1) == 0 ) /*0x4e85b*/
      goto LABEL_75; /*0x4e85b*/
    goto LABEL_94; /*0x4e85b*/
  }
LABEL_93:
  operator delete(__src); /*0x4e941*/
  if ( (v76 & 1) == 0 ) /*0x4e954*/
  {
LABEL_75:
    if ( (__dst[0] & 1) == 0 ) /*0x4e868*/
      goto LABEL_76; /*0x4e868*/
    goto LABEL_95; /*0x4e868*/
  }
LABEL_94:
  operator delete(v77); /*0x4e95a*/
  if ( (__dst[0] & 1) == 0 ) /*0x4e96d*/
  {
LABEL_76:
    if ( (v69 & 1) == 0 ) /*0x4e875*/
      goto LABEL_77; /*0x4e875*/
    goto LABEL_96; /*0x4e875*/
  }
LABEL_95:
  operator delete(v73); /*0x4e973*/
  if ( (v69 & 1) == 0 ) /*0x4e986*/
  {
LABEL_77:
    if ( (*(_BYTE *)&v80.__r_.__value_.__s.0 & 1) == 0 ) /*0x4e882*/
      goto LABEL_78; /*0x4e882*/
    goto LABEL_97; /*0x4e882*/
  }
LABEL_96:
  operator delete(v71); /*0x4e98c*/
  if ( (*(_BYTE *)&v80.__r_.__value_.__s.0 & 1) == 0 ) /*0x4e99f*/
  {
LABEL_78:
    if ( (BYTE4(v107[1]) & 1) == 0 ) /*0x4e88c*/
      goto LABEL_79; /*0x4e88c*/
    goto LABEL_98; /*0x4e88c*/
  }
LABEL_97:
  operator delete(v80.__r_.__value_.__l.__data_); /*0x4e9a5*/
  if ( (BYTE4(v107[1]) & 1) == 0 ) /*0x4e9b5*/
  {
LABEL_79:
    if ( (BYTE4(v106) & 1) == 0 ) /*0x4e896*/
      goto LABEL_81; /*0x4e896*/
    goto LABEL_80; /*0x4e896*/
  }
LABEL_98:
  operator delete(*(void **)&v108[12]); /*0x4e9bb*/
  if ( (BYTE4(v106) & 1) != 0 ) /*0x4e9c8*/
LABEL_80:
    operator delete(*(void **)((char *)v107 + 4)); /*0x4e898*/
LABEL_81:
  v62 = (void **)v104; /*0x4e8a1*/
  if ( v104 ) /*0x4e8ab*/
  {
    v63 = v105; /*0x4e8b1*/
    if ( v105 == v104 ) /*0x4e8bb*/
    {
      v64 = v104; /*0x4e8bd*/
    }
    else
    {
      do /*0x4e8d6*/
      {
        if ( (*(_BYTE *)(v63 - 3) & 1) != 0 ) /*0x4e8e0*/
          operator delete(*(v63 - 1)); /*0x4e8e6*/
        if ( (*(_BYTE *)(v63 - 6) & 1) != 0 ) /*0x4e8ef*/
          operator delete(*(v63 - 4)); /*0x4e8f5*/
        v65 = v63 - 9; /*0x4e8fa*/
        if ( (*(_BYTE *)(v63 - 9) & 1) != 0 ) /*0x4e902*/
          operator delete(*(v63 - 7)); /*0x4e908*/
        v63 -= 9; /*0x4e8d0*/
      }
      while ( v65 != v62 ); /*0x4e8d6*/
      v64 = v104; /*0x4e9d3*/
    }
    v105 = v62; /*0x4e9da*/
    operator delete(v64); /*0x4e9e1*/
  }
  return __stack_chk_guard; /*0x4e9f6*/
}
