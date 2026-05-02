// 0x23940 @ 0x23940
__int64 __fastcall ClientManager::AddCagAndInternalParm(ClientManager *a1, unsigned __int8 *a2, int a3, _DWORD *a4)
{
  unsigned __int64 v4; // r15
  __int64 v5; // r15
  unsigned __int8 *v6; // r14
  std::string *v7; // rbx
  int v8; // r13d
  std::string *v9; // rax
  __int64 v10; // rdx
  unsigned __int8 *data; // rax
  int v12; // r13d
  bool v13; // zf
  int v14; // eax
  std::string::size_type v15; // r12
  std::string::value_type *i; // rax
  std::string *v17; // rax
  int v18; // ecx
  int v19; // ecx
  std::string::size_type v20; // rcx
  std::string *v21; // r13
  int v22; // r12d
  ClientManager *v23; // r14
  int v24; // eax
  std::string *v25; // rax
  const std::string::value_type *v26; // rsi
  std::string::size_type size; // rdx
  _DWORD *v28; // r12
  unsigned int v29; // ebx
  __int64 v30; // rbx
  int v31; // eax
  const void *v32; // r15
  size_t v33; // rax
  std::string::size_type v34; // r14
  char *v35; // r12
  std::string *v36; // rax
  const std::string::value_type *v37; // rsi
  std::string::size_type v38; // rdx
  std::string *v39; // rax
  const std::string::value_type *v40; // rsi
  std::string::size_type v41; // rdx
  std::string *v42; // rax
  const std::string::value_type *v43; // rsi
  std::string::size_type v44; // rdx
  const char *v46; // rbx
  size_t v47; // rax
  size_t v48; // r15
  std::string::value_type *v49; // r12
  size_t v50; // r14
  unsigned int v51; // ebx
  unsigned int v52; // r15d
  size_t v53; // rbx
  int v54; // ebx
  const char *v55; // r14
  size_t v56; // rax
  std::string::size_type v57; // r15
  char *v58; // r12
  size_t v59; // rbx
  const void *v60; // r15
  void *v61; // rdi
  size_t v62; // rax
  std::string::size_type v63; // r14
  char *v64; // r12
  size_t v65; // rbx
  unsigned __int64 v66; // r15
  const std::string::value_type *v67; // rsi
  std::string::size_type v68; // rdx
  std::string *v69; // rax
  const std::string::value_type *v70; // rsi
  std::string::size_type v71; // rdx
  std::string *v72; // rax
  const std::string::value_type *v73; // rsi
  std::string::size_type v74; // rdx
  std::string *v75; // rax
  std::string *v76; // rax
  __int64 v77; // r15
  const char *v78; // r15
  size_t v79; // rax
  std::string::size_type v80; // r12
  char *v81; // rbx
  std::string::value_type *v82; // rbx
  size_t v83; // r14
  std::__shared_weak_count *v84; // rbx
  std::__shared_weak_count *v85; // rbx
  std::string v86; // [rsp+18h] [rbp-2E8h] BYREF
  std::string v87; // [rsp+30h] [rbp-2D0h] BYREF
  char v88[16]; // [rsp+48h] [rbp-2B8h] BYREF
  void *v89; // [rsp+58h] [rbp-2A8h]
  char v90[16]; // [rsp+60h] [rbp-2A0h] BYREF
  void *v91; // [rsp+70h] [rbp-290h]
  std::string v92; // [rsp+78h] [rbp-288h] BYREF
  std::string v93; // [rsp+90h] [rbp-270h] BYREF
  std::string v94; // [rsp+A8h] [rbp-258h] BYREF
  std::allocator<char> *__a; // [rsp+C0h] [rbp-240h]
  __int16 v96; // [rsp+C8h] [rbp-238h] BYREF
  char v97; // [rsp+CAh] [rbp-236h]
  void *v98; // [rsp+D8h] [rbp-228h]
  __int128 v99; // [rsp+E0h] [rbp-220h] BYREF
  void *v100; // [rsp+F0h] [rbp-210h]
  __int128 v101; // [rsp+100h] [rbp-200h] BYREF
  void *v102; // [rsp+110h] [rbp-1F0h]
  __int128 v103; // [rsp+120h] [rbp-1E0h] BYREF
  void *v104; // [rsp+130h] [rbp-1D0h]
  std::string __str; // [rsp+138h] [rbp-1C8h] BYREF
  char v106; // [rsp+150h] [rbp-1B0h] BYREF
  _BYTE v107[23]; // [rsp+151h] [rbp-1AFh] BYREF
  void *v108[3]; // [rsp+168h] [rbp-198h] BYREF
  char v109; // [rsp+180h] [rbp-180h] BYREF
  char v110[23]; // [rsp+181h] [rbp-17Fh] BYREF
  std::string v111; // [rsp+198h] [rbp-168h] BYREF
  char v112; // [rsp+1B0h] [rbp-150h] BYREF
  _BYTE v113[23]; // [rsp+1B1h] [rbp-14Fh] BYREF
  char v114; // [rsp+1C8h] [rbp-138h] BYREF
  char v115[15]; // [rsp+1C9h] [rbp-137h] BYREF
  void *v116; // [rsp+1D8h] [rbp-128h]
  __int64 v117; // [rsp+1E0h] [rbp-120h] BYREF
  std::__shared_weak_count *v118; // [rsp+1E8h] [rbp-118h]
  std::string v119; // [rsp+1F0h] [rbp-110h] BYREF
  unsigned int v120; // [rsp+208h] [rbp-F8h] BYREF
  int v121; // [rsp+20Ch] [rbp-F4h]
  std::string v122; // [rsp+210h] [rbp-F0h] BYREF
  ClientManager *v123; // [rsp+228h] [rbp-D8h]
  _DWORD *v124; // [rsp+230h] [rbp-D0h]
  int v125[2]; // [rsp+238h] [rbp-C8h]
  std::string v126; // [rsp+240h] [rbp-C0h] BYREF
  std::string v127; // [rsp+260h] [rbp-A0h] BYREF
  std::string v128; // [rsp+280h] [rbp-80h] BYREF
  int __val; // [rsp+29Ch] [rbp-64h] BYREF
  std::string __dst; // [rsp+2A0h] [rbp-60h] BYREF
  std::string::value_type __s[16]; // [rsp+2C0h] [rbp-40h] BYREF
  void *__p; // [rsp+2D0h] [rbp-30h]

  v125[0] = a3; /*0x23954*/
  v123 = a1; /*0x2395a*/
  __val = 0; /*0x23961*/
  *(_WORD *)&v122.__r_.__value_.__l.0 = 0; /*0x23968*/
  v4 = *a2; /*0x23971*/
  __a = (std::allocator<char> *)a2; /*0x23979*/
  v124 = a4; /*0x23980*/
  if ( (v4 & 1) != 0 ) /*0x23987*/
  {
    v5 = *((_QWORD *)a2 + 1); /*0x23989*/
    v6 = (unsigned __int8 *)*((_QWORD *)a2 + 2); /*0x2398d*/
  }
  else
  {
    v5 = v4 >> 1; /*0x23993*/
    v6 = a2 + 1; /*0x23996*/
  }
  v7 = (std::string *)&v6[v5]; /*0x2399a*/
  v8 = (_DWORD)v6 + v5; /*0x2399e*/
  v9 = (std::string *)&v6[v5]; /*0x239a1*/
  if ( v5 >= 7 ) /*0x239a8*/
  {
    v10 = v5; /*0x239b6*/
    data = v6; /*0x239b9*/
    while ( 1 ) /*0x239cc*/
    {
      v9 = (std::string *)memchr(data, 45, v10 - 6); /*0x239cc*/
      if ( !v9 ) /*0x239d4*/
      {
LABEL_9:
        v8 = (_DWORD)v6 + v5; /*0x239f4*/
        v9 = (std::string *)&v6[v5]; /*0x239f7*/
        goto LABEL_11; /*0x239fa*/
      }
      if ( !(*(_DWORD *)&v9->__r_.__value_.__l.0 ^ 0x6D762D2D /*0x239e1*/
           | *(_DWORD *)((char *)v9->__r_.__value_.__r.__words + 3) ^ 0x2064696D) )
        break; /*0x239e1*/
      data = (unsigned __int8 *)v9->__r_.__value_.__s.__data_; /*0x239e5*/
      v10 = (char *)v7 - (char *)data; /*0x239eb*/
      if ( (char *)v7 - (char *)data <= 6 ) /*0x239f2*/
        goto LABEL_9; /*0x239f2*/
    }
    v8 = (int)v9; /*0x239fc*/
  }
LABEL_11:
  v12 = v8 - (_DWORD)v6; /*0x239ff*/
  v13 = v9 == v7; /*0x23a02*/
  v14 = -1; /*0x23a05*/
  if ( v13 ) /*0x23a0c*/
    v12 = -1; /*0x23a0c*/
  v15 = v12 + 7; /*0x23a14*/
  if ( v5 >= v15 ) /*0x23a1a*/
  {
    for ( i = (std::string::value_type *)&v6[v12 + 7]; ; i = v17->__r_.__value_.__s.__data_ ) /*0x23a1c*/
    {
      if ( (char *)v7 - i <= 0 || (v17 = (std::string *)memchr(i, 32, (char *)v7 - i)) == 0 ) /*0x23a3b*/
      {
        v18 = (_DWORD)v6 + v5; /*0x23a47*/
        v17 = (std::string *)&v6[v5]; /*0x23a4a*/
        goto LABEL_21; /*0x23a4d*/
      }
      if ( *(_BYTE *)&v17->__r_.__value_.__s.0 == 32 ) /*0x23a40*/
        break; /*0x23a40*/
    }
    v18 = (int)v17; /*0x23a4f*/
LABEL_21:
    v19 = v18 - (_DWORD)v6; /*0x23a52*/
    v13 = v17 == v7; /*0x23a55*/
    v14 = -1; /*0x23a58*/
    if ( !v13 ) /*0x23a5f*/
      v14 = v19; /*0x23a5f*/
  }
  v20 = v14 - v12 - 7; /*0x23a69*/
  v21 = (std::string *)__a; /*0x23a73*/
  std::string::basic_string(&__str, (const std::string *)__a, v15, v20, __a); /*0x23a83*/
  v22 = 0; /*0x23a88*/
  v23 = v123; /*0x23a92*/
  if ( v125[0] == 2 ) /*0x23a99*/
  {
    v24 = v124[1389]; /*0x23aa2*/
    if ( v24 != 1 ) /*0x23aab*/
    {
      if ( v24 != 2 ) /*0x23ab0*/
        goto LABEL_28; /*0x23ab0*/
      v24 = 4; /*0x23ab2*/
    }
    __val = v24; /*0x23ab7*/
    v22 = v24; /*0x23aba*/
  }
LABEL_28:
  if ( *((_DWORD *)v123 + 2336) == 2 ) /*0x23ac5*/
  {
    std::operator+<char>(&__dst, " --ag-ip ", v124 + 1374); /*0x23ae4*/
    v25 = std::string::append(&__dst, " --ag-port "); /*0x23af4*/
    v126 = *v25; /*0x23afd*/
    *(_OWORD *)&v25->__r_.__value_.__l.0 = 0; /*0x23b11*/
    v25->__r_.__value_.__r.__words[2] = 0; /*0x23b14*/
    std::to_string(&v128, v124[1380]); /*0x23b2d*/
    if ( (*(_BYTE *)&v128.__r_.__value_.__s.0 & 1) != 0 ) /*0x23b39*/
    {
      v26 = v128.__r_.__value_.__l.__data_; /*0x23b3f*/
      size = v128.__r_.__value_.__l.__size_; /*0x23b43*/
    }
    else
    {
      size = (unsigned __int64)*(_BYTE *)&v128.__r_.__value_.__l.0 >> 1; /*0x23c64*/
      v26 = v128.__r_.__value_.__s.__data_; /*0x23c67*/
    }
    v36 = std::string::append(&v126, v26, size); /*0x23c72*/
    __p = v36->__r_.__value_.__l.__data_; /*0x23c7b*/
    *(_OWORD *)__s = *(_OWORD *)&v36->__r_.__value_.__l.0; /*0x23c82*/
    *(_OWORD *)&v36->__r_.__value_.__l.0 = 0; /*0x23c89*/
    v36->__r_.__value_.__r.__words[2] = 0; /*0x23c8c*/
    if ( (__s[0] & 1) != 0 ) /*0x23c9b*/
    {
      v37 = (const std::string::value_type *)__p; /*0x23ca1*/
      v38 = *(_QWORD *)&__s[8]; /*0x23ca5*/
    }
    else
    {
      v38 = (unsigned __int64)(unsigned __int8)__s[0] >> 1; /*0x23d5e*/
      v37 = &__s[1]; /*0x23d61*/
    }
    std::string::append(v21, v37, v38); /*0x23d68*/
    if ( (__s[0] & 1) != 0 ) /*0x23d71*/
    {
      operator delete(__p); /*0x23ded*/
      if ( (*(_BYTE *)&v128.__r_.__value_.__s.0 & 1) == 0 ) /*0x23df6*/
      {
LABEL_53:
        if ( (*(_BYTE *)&v126.__r_.__value_.__s.0 & 1) == 0 ) /*0x23d80*/
          goto LABEL_54; /*0x23d80*/
        goto LABEL_60; /*0x23d80*/
      }
    }
    else if ( (*(_BYTE *)&v128.__r_.__value_.__s.0 & 1) == 0 ) /*0x23d77*/
    {
      goto LABEL_53; /*0x23d77*/
    }
    operator delete(v128.__r_.__value_.__l.__data_); /*0x23dfc*/
    if ( (*(_BYTE *)&v126.__r_.__value_.__s.0 & 1) == 0 ) /*0x23e08*/
    {
LABEL_54:
      if ( (*(_BYTE *)&__dst.__r_.__value_.__s.0 & 1) == 0 ) /*0x23d8a*/
        goto LABEL_56; /*0x23d8a*/
      goto LABEL_55; /*0x23d8a*/
    }
LABEL_60:
    operator delete(v126.__r_.__value_.__l.__data_); /*0x23e0e*/
    if ( (*(_BYTE *)&__dst.__r_.__value_.__s.0 & 1) == 0 ) /*0x23e1e*/
    {
LABEL_56:
      std::to_string(&v126, v22); /*0x23d95*/
      v42 = std::string::insert(&v126, 0, " --internal "); /*0x23db4*/
      __p = v42->__r_.__value_.__l.__data_; /*0x23dbd*/
      *(_OWORD *)__s = *(_OWORD *)&v42->__r_.__value_.__l.0; /*0x23dc4*/
      *(_OWORD *)&v42->__r_.__value_.__l.0 = 0; /*0x23dcb*/
      v42->__r_.__value_.__r.__words[2] = 0; /*0x23dce*/
      if ( (__s[0] & 1) != 0 ) /*0x23ddd*/
      {
        v43 = (const std::string::value_type *)__p; /*0x23ddf*/
        v44 = *(_QWORD *)&__s[8]; /*0x23de3*/
      }
      else
      {
        v44 = (unsigned __int64)(unsigned __int8)__s[0] >> 1; /*0x23e29*/
        v43 = &__s[1]; /*0x23e2c*/
      }
      std::string::append(v21, v43, v44); /*0x23e33*/
      if ( (__s[0] & 1) != 0 ) /*0x23e3c*/
        operator delete(__p); /*0x23e42*/
      if ( (*(_BYTE *)&v126.__r_.__value_.__s.0 & 1) != 0 ) /*0x23e4e*/
        operator delete(v126.__r_.__value_.__l.__data_); /*0x23e57*/
      LOBYTE(v7) = 1; /*0x23e5c*/
      std::string::append(v21, " --server-type hy"); /*0x23e68*/
      if ( (*(_BYTE *)&__str.__r_.__value_.__s.0 & 1) != 0 ) /*0x23e74*/
        goto LABEL_68; /*0x23e74*/
      goto LABEL_69; /*0x23e74*/
    }
LABEL_55:
    operator delete(__dst.__r_.__value_.__l.__data_); /*0x23d8c*/
    goto LABEL_56; /*0x23d90*/
  }
  VdconnInitCagVpnTool(); /*0x23b4c*/
  v28 = v124; /*0x23b51*/
  v29 = v124[1298]; /*0x23b58*/
  std::string::basic_string(&v87, &__str); /*0x23b6e*/
  ClientManager::addInnerCagAndInternalParm(v23, v29, &v87, v21, &__val); /*0x23b86*/
  if ( (*(_BYTE *)&v87.__r_.__value_.__s.0 & 1) != 0 ) /*0x23b92*/
    operator delete(v87.__r_.__value_.__l.__data_); /*0x23b9b*/
  v30 = *((_QWORD *)v23 + 2944); /*0x23ba0*/
  if ( *(_DWORD *)(v30 + 6852) != 1 ) /*0x23bae*/
  {
    std::string::basic_string(&v86, &__str); /*0x23cbc*/
    v7 = &v86; /*0x23cc1*/
    ClientManager::AddUdsVpnType(v23, &v86, &__val); /*0x23cd2*/
    if ( (*(_BYTE *)&v86.__r_.__value_.__s.0 & 1) == 0 ) /*0x23cde*/
      goto LABEL_46; /*0x23cde*/
    goto LABEL_45; /*0x23cde*/
  }
  v31 = *(_DWORD *)(v30 + 6860); /*0x23bb4*/
  if ( !v31 ) /*0x23bbc*/
  {
    v46 = (const char *)(v30 + 9904); /*0x23eeb*/
    v47 = strlen(v46); /*0x23ef5*/
    if ( v47 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x23efe*/
      std::string::__throw_length_error[abi:v15006](__s); /*0x24b3e*/
    v48 = v47; /*0x23f04*/
    if ( v47 >= 0x17 ) /*0x23f0b*/
    {
      v50 = (v47 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x23f26*/
      v49 = (std::string::value_type *)operator new(v50); /*0x23f32*/
      __p = v49; /*0x23f35*/
      *(_QWORD *)__s = v50 | 1; /*0x23f3d*/
      *(_QWORD *)&__s[8] = v48; /*0x23f41*/
      v23 = v123; /*0x23f45*/
    }
    else
    {
      __s[0] = 2 * v47; /*0x23f11*/
      v49 = &__s[1]; /*0x23f14*/
      if ( !v47 ) /*0x23f1b*/
        goto LABEL_85; /*0x23f1b*/
    }
    memmove(v49, v46, v48); /*0x23f55*/
LABEL_85:
    v49[v48] = 0; /*0x23f5a*/
    if ( (*(_BYTE *)&v122.__r_.__value_.__s.0 & 1) != 0 ) /*0x23f66*/
      operator delete(v122.__r_.__value_.__l.__data_); /*0x23f6f*/
    v122.__r_.__value_.__r.__words[2] = (std::string::size_type)__p; /*0x23f78*/
    *(_OWORD *)&v122.__r_.__value_.__l.0 = *(_OWORD *)__s; /*0x23f83*/
    goto LABEL_180; /*0x23f8a*/
  }
  if ( v31 != 1 ) /*0x23bc5*/
    goto LABEL_180; /*0x23bc5*/
  *(_WORD *)__s = 0; /*0x23bcb*/
  memset(&v126, 0, sizeof(v126)); /*0x23bd4*/
  v120 = -1; /*0x23be6*/
  ClientManager::SelectCagInfoForVdi(&v117, v23, (unsigned int)v28[1298], &v126, &v120); /*0x23c10*/
  if ( v117 )
  {
    v32 = (const void *)(v117 + 164); /*0x23c25*/
    v33 = strlen((const char *)(v117 + 164)); /*0x23c2f*/
    if ( v33 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x23c38*/
      std::string::__throw_length_error[abi:v15006](&__dst); /*0x24b49*/
    v34 = v33; /*0x23c3e*/
    if ( v33 >= 0x17 )
    {
      v53 = (v33 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x24174*/
      v35 = (char *)operator new(v53); /*0x24180*/
      __dst.__r_.__value_.__r.__words[2] = (std::string::size_type)v35; /*0x24183*/
      __dst.__r_.__value_.__r.__words[0] = v53 | 1; /*0x2418b*/
      __dst.__r_.__value_.__l.__size_ = v34; /*0x2418f*/
    }
    else
    {
      __dst.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)(2 * v33); /*0x23c4f*/
      v35 = __dst.__r_.__value_.__s.__data_; /*0x23c52*/
      if ( !v33 )
      {
LABEL_103:
        v35[v34] = 0; /*0x241a1*/
        if ( (__s[0] & 1) != 0 ) /*0x241aa*/
          operator delete(__p); /*0x241b0*/
        __p = __dst.__r_.__value_.__l.__data_; /*0x241b9*/
        *(_OWORD *)__s = *(_OWORD *)&__dst.__r_.__value_.__l.0; /*0x241c1*/
        v54 = *(_DWORD *)(v117 + 1732); /*0x241ce*/
        v125[0] = *(_DWORD *)v117; /*0x241de*/
        write_log(
          1,
          0,
          "AddCagAndInternalParm",
          1889,
          "CAG: get cag for VDI success, cagname:%s, cagaddr:%s, cagport:%d",
          (const char *)(v117 + 36),
          (const char *)(v117 + 164),
          v125[0]);
        v55 = (const char *)(*((_QWORD *)v123 + 2944) + 5283LL); /*0x2421a*/
        v56 = strlen(v55); /*0x24224*/
        if ( v56 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x2422d*/
          std::string::__throw_length_error[abi:v15006](&__dst); /*0x24b54*/
        v57 = v56; /*0x24233*/
        v121 = v54; /*0x24236*/
        if ( v56 >= 0x17 ) /*0x24240*/
        {
          v59 = (v56 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x2425b*/
          v58 = (char *)operator new(v59); /*0x24267*/
          __dst.__r_.__value_.__r.__words[2] = (std::string::size_type)v58; /*0x2426a*/
          __dst.__r_.__value_.__r.__words[0] = v59 | 1; /*0x24272*/
          __dst.__r_.__value_.__l.__size_ = v57; /*0x24276*/
        }
        else
        {
          __dst.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)(2 * v56); /*0x24246*/
          v58 = __dst.__r_.__value_.__s.__data_; /*0x24249*/
          if ( !v56 ) /*0x24250*/
          {
LABEL_111:
            v58[v57] = 0; /*0x24288*/
            if ( !std::string::compare(&__dst, "en") ) /*0x2429f*/
            {
              v61 = &v128; /*0x242e7*/
              std::string::basic_string[abi:v15006]<decltype(nullptr)>(&v128, v117 + 100); /*0x242eb*/
              v28 = v124; /*0x242f0*/
              v23 = v123; /*0x242fe*/
              if ( (*(_BYTE *)&v122.__r_.__value_.__s.0 & 1) != 0 ) /*0x24305*/
              {
                v61 = v122.__r_.__value_.__l.__data_; /*0x24307*/
                operator delete(v122.__r_.__value_.__l.__data_); /*0x2430e*/
              }
              v122 = v128; /*0x24317*/
              goto LABEL_124; /*0x24329*/
            }
            v60 = (const void *)(v117 + 36); /*0x242a8*/
            v61 = (void *)(v117 + 36); /*0x242ac*/
            v62 = strlen((const char *)(v117 + 36)); /*0x242af*/
            if ( v62 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x242b8*/
              std::string::__throw_length_error[abi:v15006](&v128); /*0x24b5f*/
            v63 = v62; /*0x242be*/
            if ( v62 >= 0x17 ) /*0x242c5*/
            {
              v65 = (v62 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x24332*/
              v64 = (char *)operator new(v65); /*0x2433e*/
              v128.__r_.__value_.__r.__words[2] = (std::string::size_type)v64; /*0x24341*/
              v128.__r_.__value_.__r.__words[0] = v65 | 1; /*0x24349*/
              v128.__r_.__value_.__l.__size_ = v63; /*0x2434d*/
            }
            else
            {
              v128.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)(2 * v62); /*0x242cb*/
              v64 = v128.__r_.__value_.__s.__data_; /*0x242ce*/
              if ( !v62 ) /*0x242d5*/
                goto LABEL_121; /*0x242d5*/
            }
            v61 = v64; /*0x24351*/
            memmove(v64, v60, v63); /*0x2435a*/
LABEL_121:
            v64[v63] = 0; /*0x2435f*/
            if ( (*(_BYTE *)&v122.__r_.__value_.__s.0 & 1) != 0 ) /*0x2436b*/
            {
              v61 = v122.__r_.__value_.__l.__data_; /*0x2436d*/
              operator delete(v122.__r_.__value_.__l.__data_); /*0x24374*/
            }
            v122 = v128; /*0x2437d*/
            v23 = v123; /*0x2438f*/
            v28 = v124; /*0x24396*/
LABEL_124:
            ClientManager::AddCagSelectInfoParm(v61, v21, &v126, v120); /*0x2439d*/
            goto LABEL_125; /*0x243ad*/
          }
        }
        memmove(v58, v55, v57); /*0x24283*/
        goto LABEL_111; /*0x24283*/
      }
    }
    memmove(v35, v32, v34); /*0x2419c*/
    goto LABEL_103; /*0x2419c*/
  }
  CharToString(v88); /*0x23f9d*/
  v51 = *((_DWORD *)v23 + 472); /*0x23fa2*/
  v52 = *((_DWORD *)v23 + 8817); /*0x23fa9*/
  CharToString(v90); /*0x23fbe*/
  telnetCagConnectPoolNet(&__dst, v88, v51, v52, v90); /*0x23fda*/
  if ( (__s[0] & 1) != 0 ) /*0x23fe3*/
    operator delete(__p); /*0x23fe9*/
  __p = __dst.__r_.__value_.__l.__data_; /*0x23ff2*/
  *(_OWORD *)__s = *(_OWORD *)&__dst.__r_.__value_.__l.0; /*0x23ffa*/
  *(_WORD *)&__dst.__r_.__value_.__l.0 = 0; /*0x23ffe*/
  if ( (v90[0] & 1) != 0 ) /*0x2400b*/
    operator delete(v91); /*0x24014*/
  if ( (v88[0] & 1) != 0 ) /*0x24020*/
    operator delete(v89); /*0x24029*/
  v125[0] = *((_DWORD *)v23 + 472); /*0x24035*/
  *(_WORD *)&__dst.__r_.__value_.__l.0 = 0; /*0x2403b*/
  v106 = 18; /*0x24041*/
  strcpy(v107, "portSplit"); /*0x24052*/
  strcpy((char *)v108, "\"portProtocolValue"); /*0x24062*/
  v100 = operator new(0x20u); /*0x2408a*/
  v99 = xmmword_207430; /*0x24098*/
  strcpy((char *)v100, "../config/CommonTerminal.ini"); /*0x240b1*/
  ReadStringFromConfigFile(&v106, v108, &__dst, &v99, 0, 1); /*0x240da*/
  if ( (v99 & 1) == 0 ) /*0x240e6*/
  {
    if ( ((__int64)v108[0] & 1) == 0 ) /*0x240f3*/
      goto LABEL_96; /*0x240f3*/
LABEL_203:
    operator delete(v108[2]); /*0x24b1c*/
    if ( (v106 & 1) == 0 ) /*0x24b2f*/
      goto LABEL_98; /*0x24b2f*/
    goto LABEL_97; /*0x24b2f*/
  }
  operator delete(v100); /*0x24b0a*/
  if ( ((__int64)v108[0] & 1) != 0 ) /*0x24b16*/
    goto LABEL_203; /*0x24b16*/
LABEL_96:
  if ( (v106 & 1) != 0 ) /*0x24100*/
LABEL_97:
    operator delete(*(void **)&v107[15]); /*0x24102*/
LABEL_98:
  std::string::basic_string(&v92, &__dst); /*0x2410e*/
  v121 = stringToInt(&v92, 0); /*0x2412c*/
  if ( (*(_BYTE *)&v92.__r_.__value_.__s.0 & 1) != 0 ) /*0x24139*/
    operator delete(v92.__r_.__value_.__l.__data_); /*0x24142*/
  write_log(3, 0, "AddCagAndInternalParm", 1909, "CAG: get cag for VDI failed,telnetCagConnectPoolNet !");
LABEL_125:
  if ( (*(_BYTE *)&__dst.__r_.__value_.__s.0 & 1) != 0 ) /*0x243b6*/
    operator delete(__dst.__r_.__value_.__l.__data_); /*0x243bc*/
  if ( (__s[0] & 1) != 0 )
  {
    v66 = *(_QWORD *)&__s[8]; /*0x243cc*/
    if ( *(_QWORD *)&__s[8] ) /*0x243d3*/
      goto LABEL_129; /*0x243d3*/
LABEL_132:
    write_log(3, 0, "AddCagAndInternalParm", 1913, "CAG: get cag for VDI failed!");
    goto LABEL_174; /*0x24446*/
  }
  v66 = (unsigned __int64)(unsigned __int8)__s[0] >> 1; /*0x2441d*/
  if ( !v66 ) /*0x24423*/
    goto LABEL_132; /*0x24423*/
LABEL_129:
  std::operator+<char>(&v128, " --ag-ip ", __s); /*0x243d5*/
  ClientManager::addVdiPort((ClientManager *)&v127, (int)" --ag-ip ", v125[0]); /*0x243fc*/
  if ( (*(_BYTE *)&v127.__r_.__value_.__s.0 & 1) != 0 ) /*0x2440b*/
  {
    v67 = v127.__r_.__value_.__l.__data_; /*0x2440d*/
    v68 = v127.__r_.__value_.__l.__size_; /*0x24414*/
  }
  else
  {
    v68 = (unsigned __int64)*(_BYTE *)&v127.__r_.__value_.__l.0 >> 1; /*0x2444b*/
    v67 = v127.__r_.__value_.__s.__data_; /*0x2444e*/
  }
  v69 = std::string::append(&v128, v67, v68); /*0x24459*/
  __dst = *v69; /*0x24462*/
  *(_OWORD *)&v69->__r_.__value_.__l.0 = 0; /*0x24470*/
  v69->__r_.__value_.__r.__words[2] = 0; /*0x24473*/
  if ( (*(_BYTE *)&__dst.__r_.__value_.__s.0 & 1) != 0 ) /*0x24482*/
  {
    v70 = __dst.__r_.__value_.__l.__data_; /*0x24484*/
    v71 = __dst.__r_.__value_.__l.__size_; /*0x24488*/
  }
  else
  {
    v71 = (unsigned __int64)*(_BYTE *)&__dst.__r_.__value_.__l.0 >> 1; /*0x2448e*/
    v70 = __dst.__r_.__value_.__s.__data_; /*0x24491*/
  }
  std::string::append(v21, v70, v71); /*0x24498*/
  if ( (*(_BYTE *)&__dst.__r_.__value_.__s.0 & 1) != 0 ) /*0x244a1*/
  {
    operator delete(__dst.__r_.__value_.__l.__data_); /*0x24542*/
    if ( (*(_BYTE *)&v127.__r_.__value_.__s.0 & 1) == 0 ) /*0x2454e*/
    {
LABEL_139:
      if ( (*(_BYTE *)&v128.__r_.__value_.__s.0 & 1) == 0 ) /*0x244b8*/
        goto LABEL_141; /*0x244b8*/
      goto LABEL_140; /*0x244b8*/
    }
  }
  else if ( (*(_BYTE *)&v127.__r_.__value_.__s.0 & 1) == 0 ) /*0x244ae*/
  {
    goto LABEL_139; /*0x244ae*/
  }
  operator delete(v127.__r_.__value_.__l.__data_); /*0x2455b*/
  if ( (*(_BYTE *)&v128.__r_.__value_.__s.0 & 1) != 0 ) /*0x24564*/
LABEL_140:
    operator delete(v128.__r_.__value_.__l.__data_); /*0x244ba*/
LABEL_141:
  std::operator+<char>(&v119, "{\"cag\":\"", __s); /*0x244c3*/
  v72 = std::string::append(&v119, "\",\"port\":\""); /*0x244e8*/
  v127 = *v72; /*0x244f1*/
  *(_OWORD *)&v72->__r_.__value_.__l.0 = 0; /*0x24505*/
  v72->__r_.__value_.__r.__words[2] = 0; /*0x24508*/
  std::to_string(&v111, v125[0]); /*0x2451d*/
  if ( (*(_BYTE *)&v111.__r_.__value_.__s.0 & 1) != 0 ) /*0x2452c*/
  {
    v73 = v111.__r_.__value_.__l.__data_; /*0x2452e*/
    v74 = v111.__r_.__value_.__l.__size_; /*0x24535*/
  }
  else
  {
    v74 = (unsigned __int64)*(_BYTE *)&v111.__r_.__value_.__l.0 >> 1; /*0x2456f*/
    v73 = v111.__r_.__value_.__s.__data_; /*0x24572*/
  }
  v75 = std::string::append(&v127, v73, v74); /*0x24580*/
  v128 = *v75; /*0x24589*/
  *(_OWORD *)&v75->__r_.__value_.__l.0 = 0; /*0x24597*/
  v75->__r_.__value_.__r.__words[2] = 0; /*0x2459a*/
  v76 = std::string::append(&v128, "\"}"); /*0x245ad*/
  __dst = *v76; /*0x245b6*/
  *(_OWORD *)&v76->__r_.__value_.__l.0 = 0; /*0x245c4*/
  v76->__r_.__value_.__r.__words[2] = 0; /*0x245c7*/
  if ( (*(_BYTE *)&v128.__r_.__value_.__s.0 & 1) != 0 ) /*0x245d3*/
  {
    operator delete(v128.__r_.__value_.__l.__data_); /*0x246a7*/
    if ( (*(_BYTE *)&v111.__r_.__value_.__s.0 & 1) == 0 ) /*0x246b3*/
    {
LABEL_149:
      if ( (*(_BYTE *)&v127.__r_.__value_.__s.0 & 1) == 0 ) /*0x245ed*/
        goto LABEL_150; /*0x245ed*/
      goto LABEL_159; /*0x245ed*/
    }
  }
  else if ( (*(_BYTE *)&v111.__r_.__value_.__s.0 & 1) == 0 ) /*0x245e0*/
  {
    goto LABEL_149; /*0x245e0*/
  }
  operator delete(v111.__r_.__value_.__l.__data_); /*0x246c0*/
  if ( (*(_BYTE *)&v127.__r_.__value_.__s.0 & 1) == 0 ) /*0x246cc*/
  {
LABEL_150:
    if ( (*(_BYTE *)&v119.__r_.__value_.__s.0 & 1) == 0 ) /*0x245fa*/
      goto LABEL_152; /*0x245fa*/
    goto LABEL_151; /*0x245fa*/
  }
LABEL_159:
  operator delete(v127.__r_.__value_.__l.__data_); /*0x246d2*/
  if ( (*(_BYTE *)&v119.__r_.__value_.__s.0 & 1) != 0 ) /*0x246e5*/
LABEL_151:
    operator delete(v119.__r_.__value_.__l.__data_); /*0x245fc*/
LABEL_152:
  CTraceManager::getVdnumKey(&v128, v28[1299]); /*0x24608*/
  *(_QWORD *)v125 = v66; /*0x24619*/
  CTraceManager::add((unsigned int)&v119, 2, 21, (unsigned int)&__dst, (unsigned int)&v128, v28[1299] != 0, -1); /*0x24650*/
  v77 = *((_QWORD *)v23 + 495); /*0x24655*/
  if ( v77 ) /*0x2465f*/
  {
    v78 = (const char *)(v77 + 4); /*0x24665*/
    v79 = strlen(v78); /*0x2466c*/
    if ( v79 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x24675*/
      std::string::__throw_length_error[abi:v15006](&v127); /*0x24b6d*/
    v80 = v79; /*0x2467b*/
    if ( v79 >= 0x17 ) /*0x24682*/
    {
      v83 = (v79 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x24705*/
      v81 = (char *)operator new(v83); /*0x24711*/
      v127.__r_.__value_.__r.__words[2] = (std::string::size_type)v81; /*0x24714*/
      v127.__r_.__value_.__r.__words[0] = v83 | 1; /*0x2471f*/
      v127.__r_.__value_.__l.__size_ = v80; /*0x24726*/
      v23 = v123; /*0x2472d*/
    }
    else
    {
      v127.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)(2 * v79); /*0x24688*/
      v81 = v127.__r_.__value_.__s.__data_; /*0x2468e*/
      if ( !v79 ) /*0x24698*/
        goto LABEL_164; /*0x24698*/
    }
    memmove(v81, v78, v80); /*0x2473d*/
LABEL_164:
    v82 = &v81[v80]; /*0x24742*/
    v28 = v124; /*0x24745*/
    goto LABEL_165; /*0x24745*/
  }
  v127.__r_.__value_.__s.0 = 0; /*0x246f0*/
  v82 = v127.__r_.__value_.__s.__data_; /*0x246f7*/
LABEL_165:
  *v82 = 0; /*0x2474c*/
  CTraceManager::setUserNo(&v119, &v127); /*0x2475d*/
  v66 = *(_QWORD *)v125; /*0x24762*/
  if ( (*(_BYTE *)&v127.__r_.__value_.__s.0 & 1) != 0 ) /*0x24770*/
    operator delete(v127.__r_.__value_.__l.__data_); /*0x24779*/
  CTraceManager::setVmid(&v119, v28 + 1654); /*0x2478f*/
  CTraceManager::upload(&v119); /*0x2479b*/
  ClientManager::AddRtnInnerCagParm(v23, v21); /*0x247a6*/
  v84 = (std::__shared_weak_count *)v119.__r_.__value_.__l.__size_; /*0x247ab*/
  if ( v119.__r_.__value_.__l.__size_ /*0x247be*/
    && !_InterlockedExchangeAdd64((volatile signed __int64 *)(v119.__r_.__value_.__l.__size_ + 8), 0xFFFFFFFFFFFFFFFFLL) )
  {
    ((void (__fastcall *)(std::__shared_weak_count *))v84->__on_zero_shared)(v84); /*0x247cf*/
    std::__shared_weak_count::__release_weak(v84); /*0x247d5*/
  }
  if ( (*(_BYTE *)&v128.__r_.__value_.__s.0 & 1) != 0 ) /*0x247de*/
    operator delete(v128.__r_.__value_.__l.__data_); /*0x247e4*/
  if ( (*(_BYTE *)&__dst.__r_.__value_.__s.0 & 1) != 0 ) /*0x247ed*/
    operator delete(__dst.__r_.__value_.__l.__data_); /*0x247f3*/
LABEL_174:
  v85 = v118; /*0x247f8*/
  if ( v118 && !_InterlockedExchangeAdd64(&v118->__shared_owners_, 0xFFFFFFFFFFFFFFFFLL) ) /*0x2480b*/
  {
    ((void (__fastcall *)(std::__shared_weak_count *))v85->__on_zero_shared)(v85); /*0x2481c*/
    std::__shared_weak_count::__release_weak(v85); /*0x24822*/
  }
  if ( (*(_BYTE *)&v126.__r_.__value_.__s.0 & 1) == 0 ) /*0x2482e*/
  {
    if ( (__s[0] & 1) == 0 ) /*0x24838*/
      goto LABEL_179; /*0x24838*/
    goto LABEL_199; /*0x24838*/
  }
  operator delete(v126.__r_.__value_.__l.__data_); /*0x24ace*/
  if ( (__s[0] & 1) != 0 ) /*0x24ad7*/
  {
LABEL_199:
    operator delete(__p); /*0x24add*/
    if ( !v66 ) /*0x24ae9*/
      goto LABEL_200; /*0x24ae9*/
LABEL_180:
    std::string::basic_string(&v93, &__str); /*0x24847*/
    v112 = 22; /*0x2485a*/
    strcpy(v113, "GatewayName"); /*0x2486b*/
    std::string::basic_string(&v94, &v122); /*0x24891*/
    v102 = operator new(0x20u); /*0x248a0*/
    v101 = xmmword_2073B0; /*0x248ae*/
    strcpy((char *)v102, "../config/Communication.ini"); /*0x248c7*/
    WriteStringToConfigFile(&v93, &v112, &v94, &v101, 1, 1); /*0x248f6*/
    if ( (v101 & 1) != 0 ) /*0x24902*/
    {
      operator delete(v102); /*0x24a2e*/
      if ( (*(_BYTE *)&v94.__r_.__value_.__s.0 & 1) == 0 ) /*0x24a3a*/
      {
LABEL_182:
        if ( (v112 & 1) == 0 ) /*0x2491c*/
          goto LABEL_183; /*0x2491c*/
        goto LABEL_192; /*0x2491c*/
      }
    }
    else if ( (*(_BYTE *)&v94.__r_.__value_.__s.0 & 1) == 0 ) /*0x2490f*/
    {
      goto LABEL_182; /*0x2490f*/
    }
    operator delete(v94.__r_.__value_.__l.__data_); /*0x24a47*/
    if ( (v112 & 1) == 0 ) /*0x24a53*/
    {
LABEL_183:
      if ( (*(_BYTE *)&v93.__r_.__value_.__s.0 & 1) == 0 ) /*0x24929*/
        goto LABEL_185; /*0x24929*/
      goto LABEL_184; /*0x24929*/
    }
LABEL_192:
    operator delete(*(void **)&v113[15]); /*0x24a59*/
    if ( (*(_BYTE *)&v93.__r_.__value_.__s.0 & 1) == 0 ) /*0x24a6c*/
    {
LABEL_185:
      v109 = 14; /*0x24937*/
      strcpy(v110, "GATEWAY"); /*0x2493e*/
      v114 = 12; /*0x24959*/
      strcpy(v115, "UDSVPN"); /*0x24960*/
      v96 = 12290; /*0x2497a*/
      v97 = 0; /*0x24983*/
      v104 = operator new(0x20u); /*0x24994*/
      v103 = xmmword_2073B0; /*0x249a2*/
      strcpy((char *)v104, "../config/Communication.ini"); /*0x249bb*/
      v7 = (std::string *)&v109; /*0x249c2*/
      WriteStringToConfigFile(&v109, &v114, &v96, &v103, 1, 1); /*0x249ed*/
      if ( (v103 & 1) != 0 ) /*0x249f9*/
      {
        operator delete(v104); /*0x24a7e*/
        if ( (v96 & 1) == 0 ) /*0x24a8a*/
        {
LABEL_187:
          if ( (v114 & 1) == 0 ) /*0x24a0f*/
            goto LABEL_188; /*0x24a0f*/
          goto LABEL_196; /*0x24a0f*/
        }
      }
      else if ( (v96 & 1) == 0 ) /*0x24a02*/
      {
        goto LABEL_187; /*0x24a02*/
      }
      operator delete(v98); /*0x24a97*/
      if ( (v114 & 1) == 0 ) /*0x24aa3*/
      {
LABEL_188:
        if ( (v109 & 1) == 0 ) /*0x24a1c*/
          goto LABEL_46; /*0x24a1c*/
        goto LABEL_45; /*0x24a1c*/
      }
LABEL_196:
      operator delete(v116); /*0x24aa9*/
      if ( (v109 & 1) == 0 ) /*0x24abc*/
      {
LABEL_46:
        if ( *((_DWORD *)v23 + 7134) == 1 ) /*0x23cf1*/
          LOBYTE(__val) = __val | 8; /*0x23cf3*/
        ClientManager::AddCagExtranetAccsess(v23, &__val); /*0x23cfe*/
        std::to_string(&v126, __val); /*0x23d0d*/
        v39 = std::string::insert(&v126, 0, " --internal "); /*0x23d22*/
        __p = v39->__r_.__value_.__l.__data_; /*0x23d2b*/
        *(_OWORD *)__s = *(_OWORD *)&v39->__r_.__value_.__l.0; /*0x23d32*/
        *(_OWORD *)&v39->__r_.__value_.__l.0 = 0; /*0x23d39*/
        v39->__r_.__value_.__r.__words[2] = 0; /*0x23d3c*/
        if ( (__s[0] & 1) != 0 ) /*0x23d4b*/
        {
          v40 = (const std::string::value_type *)__p; /*0x23d51*/
          v41 = *(_QWORD *)&__s[8]; /*0x23d55*/
        }
        else
        {
          v41 = (unsigned __int64)(unsigned __int8)__s[0] >> 1; /*0x23eab*/
          v40 = &__s[1]; /*0x23eae*/
        }
        std::string::append(v21, v40, v41); /*0x23eb5*/
        if ( (__s[0] & 1) != 0 ) /*0x23ebe*/
          operator delete(__p); /*0x23ec4*/
        if ( (*(_BYTE *)&v126.__r_.__value_.__s.0 & 1) != 0 ) /*0x23ed0*/
          operator delete(v126.__r_.__value_.__l.__data_); /*0x23ed9*/
        LOBYTE(v7) = 1; /*0x23ede*/
        if ( (*(_BYTE *)&__str.__r_.__value_.__s.0 & 1) != 0 ) /*0x23ee7*/
          goto LABEL_68; /*0x23ee7*/
        goto LABEL_69; /*0x23ee7*/
      }
LABEL_45:
      operator delete(v7->__r_.__value_.__l.__data_); /*0x23ce0*/
      goto LABEL_46; /*0x23ce4*/
    }
LABEL_184:
    operator delete(v93.__r_.__value_.__l.__data_); /*0x2492b*/
    goto LABEL_185; /*0x24932*/
  }
LABEL_179:
  if ( v66 ) /*0x24841*/
    goto LABEL_180; /*0x24841*/
LABEL_200:
  LODWORD(v7) = 0; /*0x24aef*/
  if ( (*(_BYTE *)&__str.__r_.__value_.__s.0 & 1) != 0 ) /*0x24af8*/
LABEL_68:
    operator delete(__str.__r_.__value_.__l.__data_); /*0x23e76*/
LABEL_69:
  if ( (*(_BYTE *)&v122.__r_.__value_.__s.0 & 1) != 0 ) /*0x23e89*/
    operator delete(v122.__r_.__value_.__l.__data_); /*0x23e92*/
  return (unsigned int)v7; /*0x23e99*/
}
