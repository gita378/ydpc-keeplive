// 0x2760 @ 0x2760
__int64 __fastcall SimpleAsyncWorker::Execute(SimpleAsyncWorker *this)
{
  SimpleAsyncWorker *rdbuf; // rbx
  __int64 v2; // rax
  unsigned int v3; // edx
  char *v4; // rsi
  __int64 v5; // rdx
  __int64 v6; // r15
  const std::locale::facet *v7; // rax
  char v8; // r13
  __int64 v9; // r14
  const char *v10; // r15
  size_t v11; // rax
  __int64 v12; // r14
  const std::locale::facet *v13; // rax
  char v14; // r12
  __int64 v15; // r14
  const char *v16; // r15
  size_t v17; // rax
  __int64 v18; // r14
  const std::locale::facet *v19; // rax
  char v20; // r12
  __int64 v21; // r14
  const char *v22; // r15
  size_t v23; // rax
  __int64 v24; // r14
  const std::locale::facet *v25; // rax
  char v26; // r12
  __int64 v27; // r14
  const char *v28; // r15
  size_t v29; // rax
  __int64 v30; // r15
  const std::locale::facet *v31; // rax
  char v32; // r13
  __int64 v33; // rax
  __int64 v34; // r15
  const std::locale::facet *v35; // rax
  char v36; // r14
  __int64 v37; // r14
  const char *v38; // r15
  size_t v39; // rax
  __int64 v40; // r15
  const std::locale::facet *v41; // rax
  char v42; // r13
  __int64 v43; // rax
  __int64 v44; // r15
  const std::locale::facet *v45; // rax
  char v46; // r13
  __int64 v47; // r15
  const std::locale::facet *v48; // rax
  char v49; // r14
  size_t v50; // rax
  __int64 *v51; // r14
  char *v52; // r15
  unsigned int event_cap_low; // r13d
  __int64 *iarray; // r14
  __int64 v55; // r12
  size_t v56; // r12
  unsigned __int64 v57; // rbx
  int *v58; // r12
  int *index; // r15
  char *iarray_size; // rsi
  __int64 v61; // r15
  size_t v62; // r15
  __int64 v63; // rax
  std::ios_base::event_callback *fn; // rdx
  __int64 v65; // r14
  const std::locale::facet *v66; // rax
  char v67; // r12
  __int64 v68; // r14
  int *v69; // rax
  __int64 v70; // rdi
  char *v71; // rsi
  size_t v72; // rdx
  __int64 v73; // rax
  __int64 v74; // r14
  const std::locale::facet *v75; // rax
  char v76; // r12
  size_t v77; // rax
  std::ios_base::event_callback *v78; // r14
  int *v79; // r15
  unsigned int loc_low; // r13d
  std::ios_base::event_callback *v81; // r14
  __int64 v82; // r12
  size_t v83; // r12
  unsigned __int64 v84; // rbx
  char *v85; // r12
  char *v86; // r15
  int *v87; // rsi
  __int64 v88; // r15
  size_t v89; // r15
  __int64 v90; // rax
  std::streamsize width; // rdx
  __int64 v92; // r14
  const std::locale::facet *v93; // rax
  char v94; // r12
  void *v95; // rax
  void *v96; // r14
  char *v97; // rax
  char *v98; // rax
  int v99; // eax
  unsigned int v100; // eax
  __int64 v101; // rsi
  __int64 v102; // rax
  __int64 (__fastcall *v103)(char *, _QWORD (__fastcall *)(int, int, const char *, const char *)); // rax
  char *v104; // rbx
  _DWORD *v105; // rcx
  void *v106; // rax
  char *v107; // rdi
  __int64 v108; // r15
  const std::locale::facet *v109; // rax
  char v110; // r13
  void *v111; // rax
  char *v112; // rdi
  __int64 v113; // rax
  const char *v114; // rsi
  __int64 v115; // rdx
  unsigned int v116; // ebx
  __int64 v117; // rax
  __int64 v118; // rax
  char *v119; // rsi
  char *v120; // rdx
  char *v121; // rcx
  char *v122; // r9
  unsigned int v123; // ebx
  const char *v124; // rsi
  char *v125; // rsi
  char *v126; // rdx
  char *v127; // rcx
  char *v128; // r9
  __int64 v129; // rax
  __int64 v130; // rbx
  const std::locale::facet *v131; // rax
  char v132; // r12
  __int64 v133; // rbx
  const std::locale::facet *v134; // rax
  char v135; // r15
  std::ios_base __dst; // [rsp+0h] [rbp-880h] BYREF
  std::ios_base __src; // [rsp+450h] [rbp-430h] BYREF

  rdbuf = this; /*0x2774*/
  v2 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, "command: ", 9);
  v3 = *((unsigned __int8 *)this + 104); /*0x27a0*/
  v4 = (char *)this + 105; /*0x27a4*/
  *(_QWORD *)&__dst.__fmtflags_ = (char *)this + 105; /*0x27ab*/
  if ( (v3 & 1) != 0 ) /*0x27b2*/
  {
    v4 = (char *)*((_QWORD *)this + 15); /*0x27b4*/
    v5 = *((_QWORD *)this + 14); /*0x27b8*/
  }
  else
  {
    v5 = v3 >> 1; /*0x27be*/
  }
  v6 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v2, v4, v5); /*0x27c8*/
  std::ios_base::getloc(&__src); /*0x27df*/
  v7 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x27ee*/
  v8 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v7->__vftable[2].~facet_0)(v7, 10); /*0x2801*/
  std::locale::~locale((std::locale *)&__src); /*0x2807*/
  std::ostream::put(v6, (unsigned int)v8); /*0x2813*/
  std::ostream::flush(v6); /*0x281b*/
  v9 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, " userName: ", 11);
  if ( (*((_BYTE *)this + 128) & 1) != 0 ) /*0x283e*/
    v10 = (const char *)*((_QWORD *)this + 18); /*0x2849*/
  else
    v10 = (char *)this + 129; /*0x2840*/
  v11 = strlen(v10); /*0x2853*/
  v12 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v9, v10, v11); /*0x2866*/
  std::ios_base::getloc(&__src); /*0x287d*/
  v13 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x288c*/
  v14 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v13->__vftable[2].~facet_0)(v13, 10); /*0x289f*/
  std::locale::~locale((std::locale *)&__src); /*0x28a5*/
  std::ostream::put(v12, (unsigned int)v14); /*0x28b1*/
  std::ostream::flush(v12); /*0x28b9*/
  v15 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v12, " vmpsswd: ", 10);
  if ( (*((_BYTE *)this + 152) & 1) != 0 ) /*0x28dc*/
    v16 = (const char *)*((_QWORD *)this + 21); /*0x28e7*/
  else
    v16 = (char *)this + 153; /*0x28de*/
  v17 = strlen(v16); /*0x28f1*/
  v18 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v15, v16, v17); /*0x2904*/
  std::ios_base::getloc(&__src); /*0x291b*/
  v19 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x292a*/
  v20 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v19->__vftable[2].~facet_0)(v19, 10); /*0x293d*/
  std::locale::~locale((std::locale *)&__src); /*0x2943*/
  std::ostream::put(v18, (unsigned int)v20); /*0x294f*/
  std::ostream::flush(v18); /*0x2957*/
  v21 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v18, " vmID: ", 7);
  if ( (*((_BYTE *)this + 176) & 1) != 0 ) /*0x297a*/
    v22 = (const char *)*((_QWORD *)this + 24); /*0x2985*/
  else
    v22 = (char *)this + 177; /*0x297c*/
  v23 = strlen(v22); /*0x298f*/
  v24 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v21, v22, v23); /*0x29a2*/
  std::ios_base::getloc(&__src); /*0x29b9*/
  v25 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x29c8*/
  v26 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v25->__vftable[2].~facet_0)(v25, 10); /*0x29db*/
  std::locale::~locale((std::locale *)&__src); /*0x29e1*/
  std::ostream::put(v24, (unsigned int)v26); /*0x29ed*/
  std::ostream::flush(v24); /*0x29f5*/
  v27 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v24, " vmCIP: ", 8);
  if ( (*((_BYTE *)this + 200) & 1) != 0 ) /*0x2a18*/
    v28 = (const char *)*((_QWORD *)this + 27); /*0x2a23*/
  else
    v28 = (char *)this + 201; /*0x2a1a*/
  v29 = strlen(v28); /*0x2a2d*/
  v30 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v27, v28, v29); /*0x2a40*/
  std::ios_base::getloc(&__src); /*0x2a57*/
  v31 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x2a69*/
  v32 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v31->__vftable[2].~facet_0)(v31, 10); /*0x2a7c*/
  std::locale::~locale((std::locale *)&__src); /*0x2a82*/
  std::ostream::put(v30, (unsigned int)v32); /*0x2a8e*/
  std::ostream::flush(v30); /*0x2a96*/
  v33 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v30, " vmPort: ", 9);
  v34 = std::ostream::operator<<(v33, *((unsigned int *)this + 56)); /*0x2abd*/
  std::ios_base::getloc(&__src); /*0x2acd*/
  v35 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x2ad8*/
  v36 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v35->__vftable[2].~facet_0)(v35, 10); /*0x2aeb*/
  std::locale::~locale((std::locale *)&__src); /*0x2af1*/
  std::ostream::put(v34, (unsigned int)v36); /*0x2afd*/
  std::ostream::flush(v34); /*0x2b05*/
  v37 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v34, " cagIP: ", 8);
  if ( (*((_BYTE *)this + 232) & 1) != 0 ) /*0x2b28*/
    v38 = (const char *)*((_QWORD *)this + 31); /*0x2b33*/
  else
    v38 = (char *)this + 233; /*0x2b2a*/
  v39 = strlen(v38); /*0x2b3d*/
  v40 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v37, v38, v39); /*0x2b50*/
  std::ios_base::getloc(&__src); /*0x2b60*/
  v41 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x2b72*/
  v42 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v41->__vftable[2].~facet_0)(v41, 10); /*0x2b85*/
  std::locale::~locale((std::locale *)&__src); /*0x2b8b*/
  std::ostream::put(v40, (unsigned int)v42); /*0x2b97*/
  std::ostream::flush(v40); /*0x2b9f*/
  v43 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v40, " cagPort: ", 10);
  v44 = std::ostream::operator<<(v43, *((unsigned int *)this + 64)); /*0x2bc6*/
  std::ios_base::getloc(&__src); /*0x2bd6*/
  v45 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x2be1*/
  v46 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v45->__vftable[2].~facet_0)(v45, 10); /*0x2bf4*/
  std::locale::~locale((std::locale *)&__src); /*0x2bfa*/
  std::ostream::put(v44, (unsigned int)v46); /*0x2c06*/
  std::ostream::flush(v44); /*0x2c0e*/
  v47 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>( /*0x2c2b*/
          &std::cout,
          "********************** mac relate **********************/n",
          58);
  std::ios_base::getloc(&__src); /*0x2c3b*/
  v48 = std::locale::use_facet((const std::locale *)&__src, &std::ctype<char>::id); /*0x2c46*/
  v49 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v48->__vftable[2].~facet_0)(v48, 10); /*0x2c59*/
  std::locale::~locale((std::locale *)&__src); /*0x2c5f*/
  std::ostream::put(v47, (unsigned int)v49); /*0x2c6b*/
  std::ostream::flush(v47); /*0x2c73*/
  __dst.__rdbuf_ = this; /*0x2c8c*/
  if ( !getcwd((char *)&__src, 0x400u) ) /*0x2c93*/
  {
    perror("getcwd() error"); /*0x3358*/
    if ( chdir("../../../../chuanyunAddon-zte/ccsdk/mac/uSmartView_VDI_Client.app/Contents/Frameworks") ) /*0x3364*/
      goto LABEL_46; /*0x336b*/
    goto LABEL_49; /*0x336b*/
  }
  v50 = strlen((const char *)&__src); /*0x2ca0*/
  if ( v50 >= 0xFFFFFFFFFFFFFFF8LL ) /*0x2ca9*/
    goto LABEL_144; /*0x2ca9*/
  v51 = (__int64 *)v50; /*0x2caf*/
  if ( v50 >= 0x17 ) /*0x2cb6*/
  {
    v55 = v50 | 7; /*0x2cf8*/
    if ( (v50 | 7) == 0x17 ) /*0x2d00*/
      v55 = (v50 & 0xFFFFFFFFFFFFFFF8LL) + 8; /*0x2d00*/
    v56 = v55 + 1; /*0x2d04*/
    v52 = (char *)operator new(v56); /*0x2d0f*/
    __dst.__iarray_size_ = (size_t)v52; /*0x2d12*/
    __dst.__event_cap_ = v56 | 1; /*0x2d1d*/
    __dst.__iarray_ = v51; /*0x2d24*/
LABEL_28:
    memcpy(v52, &__src, (size_t)v51); /*0x2d2b*/
    *((_BYTE *)v51 + (_QWORD)v52) = 0; /*0x2d3d*/
    event_cap_low = LOBYTE(__dst.__event_cap_); /*0x2d42*/
    if ( (__dst.__event_cap_ & 1) != 0 ) /*0x2d4e*/
      goto LABEL_24; /*0x2d4e*/
    goto LABEL_29; /*0x2d4e*/
  }
  LOBYTE(__dst.__event_cap_) = 2 * v50; /*0x2cbc*/
  v52 = (char *)&__dst.__event_cap_ + 1; /*0x2cc2*/
  if ( v50 ) /*0x2ccc*/
    goto LABEL_28; /*0x2ccc*/
  BYTE1(__dst.__event_cap_) = 0; /*0x2cce*/
  event_cap_low = LOBYTE(__dst.__event_cap_); /*0x2cd3*/
  if ( (__dst.__event_cap_ & 1) != 0 ) /*0x2cdf*/
  {
LABEL_24:
    iarray = __dst.__iarray_; /*0x2ce1*/
    goto LABEL_30; /*0x2ce8*/
  }
LABEL_29:
  iarray = (__int64 *)(event_cap_low >> 1); /*0x2d50*/
LABEL_30:
  v57 = (unsigned __int64)(iarray + 2); /*0x2d56*/
  if ( (unsigned __int64)(iarray + 2) >= 0xFFFFFFFFFFFFFFF8LL ) /*0x2d5e*/
    goto LABEL_144; /*0x2d5e*/
  if ( v57 < 0x17 ) /*0x2d68*/
  {
    memset(&__dst.__loc_, 0, 24); /*0x2d6d*/
    LOBYTE(__dst.__loc_) = 2 * v57; /*0x2d81*/
    v58 = (int *)((char *)&__dst.__loc_ + 1); /*0x2d87*/
    index = (int *)((char *)&__dst.__loc_ + 1); /*0x2d8e*/
    rdbuf = (SimpleAsyncWorker *)__dst.__rdbuf_; /*0x2d94*/
    if ( !iarray ) /*0x2d9b*/
      goto LABEL_40; /*0x2d9b*/
    if ( (event_cap_low & 1) != 0 ) /*0x2da1*/
      goto LABEL_34; /*0x2da1*/
LABEL_38:
    iarray_size = (char *)&__dst.__event_cap_ + 1; /*0x2e01*/
    goto LABEL_39; /*0x2e01*/
  }
  v61 = v57 | 7; /*0x2dba*/
  if ( (v57 | 7) == 0x17 ) /*0x2dc2*/
    v61 = (v57 & 0xFFFFFFFFFFFFFFF8LL) + 8; /*0x2dc2*/
  v62 = v61 + 1; /*0x2dc6*/
  v58 = (int *)operator new(v62); /*0x2dd1*/
  __dst.__loc_ = (void *)(v62 | 1); /*0x2dd8*/
  __dst.__index_ = v58; /*0x2ddf*/
  __dst.__fn_ = (std::ios_base::event_callback *)(iarray + 2); /*0x2de6*/
  index = (int *)((char *)&__dst.__loc_ + 1); /*0x2ded*/
  rdbuf = (SimpleAsyncWorker *)__dst.__rdbuf_; /*0x2df4*/
  if ( (event_cap_low & 1) == 0 ) /*0x2dff*/
    goto LABEL_38; /*0x2dff*/
LABEL_34:
  iarray_size = (char *)__dst.__iarray_size_; /*0x2da3*/
LABEL_39:
  memmove(v58, iarray_size, (size_t)iarray); /*0x2e08*/
LABEL_40:
  strcpy((char *)iarray + (_QWORD)v58, "/libvdconn.dylib"); /*0x2e13*/
  v63 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(
          &std::cout,
          "The full path of ./libvdconn.dylib is: ",
          39);
  if ( ((__int64)__dst.__loc_ & 1) != 0 ) /*0x2e47*/
  {
    index = __dst.__index_; /*0x2e49*/
    fn = __dst.__fn_; /*0x2e50*/
  }
  else
  {
    fn = (std::ios_base::event_callback *)(LOBYTE(__dst.__loc_) >> 1); /*0x2e59*/
  }
  v65 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v63, index, fn); /*0x2e66*/
  std::ios_base::getloc((const std::ios_base *)&__dst.__precision_); /*0x2e7d*/
  v66 = std::locale::use_facet((const std::locale *)&__dst.__precision_, &std::ctype<char>::id); /*0x2e8c*/
  v67 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v66->__vftable[2].~facet_0)(v66, 10); /*0x2e9f*/
  std::locale::~locale((std::locale *)&__dst.__precision_); /*0x2ea5*/
  std::ostream::put(v65, (unsigned int)v67); /*0x2eb1*/
  std::ostream::flush(v65); /*0x2eb9*/
  if ( ((__int64)__dst.__loc_ & 1) == 0 ) /*0x2ec5*/
  {
    if ( (event_cap_low & 1) == 0 ) /*0x2ecb*/
      goto LABEL_45; /*0x2ecb*/
LABEL_48:
    operator delete((void *)__dst.__iarray_size_); /*0x2f2c*/
    if ( chdir("../../../../chuanyunAddon-zte/ccsdk/mac/uSmartView_VDI_Client.app/Contents/Frameworks") ) /*0x2f3f*/
      goto LABEL_46; /*0x2f46*/
    goto LABEL_49; /*0x2f46*/
  }
  operator delete(__dst.__index_); /*0x2f21*/
  if ( (event_cap_low & 1) != 0 ) /*0x2f2a*/
    goto LABEL_48; /*0x2f2a*/
LABEL_45:
  if ( chdir("../../../../chuanyunAddon-zte/ccsdk/mac/uSmartView_VDI_Client.app/Contents/Frameworks") )
  {
LABEL_46:
    v68 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(
            &std::cerr,
            "Error changing directory: ",
            26);
    v69 = __error(); /*0x2ef8*/
    v70 = v68; /*0x2f0f*/
    v71 = strerror(*v69); /*0x2f12*/
    v72 = strlen(v71); /*0x2f15*/
    goto LABEL_50; /*0x2f18*/
  }
LABEL_49:
  v73 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>( /*0x2f48*/
          &std::cout,
          "Directory changed to ",
          21);
  v71 = "../../../../chuanyunAddon-zte/ccsdk/mac/uSmartView_VDI_Client.app/Contents/Frameworks"; /*0x2f60*/
  v72 = 85; /*0x2f67*/
  v70 = v73; /*0x2f6c*/
LABEL_50:
  v74 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v70, v71, v72); /*0x2f6f*/
  std::ios_base::getloc((const std::ios_base *)&__dst.__event_cap_); /*0x2f8b*/
  v75 = std::locale::use_facet((const std::locale *)&__dst.__event_cap_, &std::ctype<char>::id); /*0x2f9a*/
  v76 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v75->__vftable[2].~facet_0)(v75, 10); /*0x2fad*/
  std::locale::~locale((std::locale *)&__dst.__event_cap_); /*0x2fb3*/
  std::ostream::put(v74, (unsigned int)v76); /*0x2fbf*/
  std::ostream::flush(v74); /*0x2fc7*/
  if ( !getcwd((char *)&__dst.__event_cap_, 0x400u) ) /*0x2fe0*/
  {
    perror("getcwd() error"); /*0x337d*/
    goto LABEL_78; /*0x3382*/
  }
  v77 = strlen((const char *)&__dst.__event_cap_); /*0x2fed*/
  if ( v77 >= 0xFFFFFFFFFFFFFFF8LL ) /*0x2ff6*/
LABEL_144:
    abort(); /*0x3795*/
  v78 = (std::ios_base::event_callback *)v77; /*0x2ffc*/
  if ( v77 >= 0x17 ) /*0x3003*/
  {
    v82 = v77 | 7; /*0x3045*/
    if ( (v77 | 7) == 0x17 ) /*0x304d*/
      v82 = (v77 & 0xFFFFFFFFFFFFFFF8LL) + 8; /*0x304d*/
    v83 = v82 + 1; /*0x3051*/
    v79 = (int *)operator new(v83); /*0x305c*/
    __dst.__index_ = v79; /*0x305f*/
    __dst.__loc_ = (void *)(v83 | 1); /*0x306a*/
    __dst.__fn_ = v78; /*0x3071*/
LABEL_59:
    memcpy(v79, &__dst.__event_cap_, (size_t)v78); /*0x3078*/
    *((_BYTE *)v78 + (_QWORD)v79) = 0; /*0x308a*/
    loc_low = LOBYTE(__dst.__loc_); /*0x308f*/
    if ( ((__int64)__dst.__loc_ & 1) != 0 ) /*0x309b*/
      goto LABEL_55; /*0x309b*/
    goto LABEL_60; /*0x309b*/
  }
  LOBYTE(__dst.__loc_) = 2 * v77; /*0x3009*/
  v79 = (int *)((char *)&__dst.__loc_ + 1); /*0x300f*/
  if ( v77 ) /*0x3019*/
    goto LABEL_59; /*0x3019*/
  BYTE1(__dst.__loc_) = 0; /*0x301b*/
  loc_low = LOBYTE(__dst.__loc_); /*0x3020*/
  if ( ((__int64)__dst.__loc_ & 1) != 0 ) /*0x302c*/
  {
LABEL_55:
    v81 = __dst.__fn_; /*0x302e*/
    goto LABEL_61; /*0x3035*/
  }
LABEL_60:
  v81 = (std::ios_base::event_callback *)(loc_low >> 1); /*0x309d*/
LABEL_61:
  v84 = (unsigned __int64)(v81 + 2); /*0x30a3*/
  if ( (unsigned __int64)(v81 + 2) >= 0xFFFFFFFFFFFFFFF8LL ) /*0x30ab*/
    goto LABEL_144; /*0x30ab*/
  if ( v84 >= 0x17 ) /*0x30b5*/
  {
    v88 = v84 | 7; /*0x3107*/
    if ( (v84 | 7) == 0x17 ) /*0x310f*/
      v88 = (v84 & 0xFFFFFFFFFFFFFFF8LL) + 8; /*0x310f*/
    v89 = v88 + 1; /*0x3113*/
    v85 = (char *)operator new(v89); /*0x311e*/
    __dst.__precision_ = v89 | 1; /*0x3125*/
    *(_QWORD *)&__dst.__rdstate_ = v85; /*0x312c*/
    __dst.__width_ = (std::streamsize)(v81 + 2); /*0x3133*/
    v86 = (char *)&__dst.__precision_ + 1; /*0x313a*/
    rdbuf = (SimpleAsyncWorker *)__dst.__rdbuf_; /*0x3141*/
    if ( (loc_low & 1) != 0 ) /*0x314c*/
      goto LABEL_65; /*0x314c*/
    goto LABEL_69; /*0x314c*/
  }
  memset(&__dst.__precision_, 0, 24); /*0x30ba*/
  LOBYTE(__dst.__precision_) = 2 * v84; /*0x30ce*/
  v85 = (char *)&__dst.__precision_ + 1; /*0x30d4*/
  v86 = (char *)&__dst.__precision_ + 1; /*0x30db*/
  rdbuf = (SimpleAsyncWorker *)__dst.__rdbuf_; /*0x30e1*/
  if ( v81 ) /*0x30e8*/
  {
    if ( (loc_low & 1) != 0 ) /*0x30ee*/
    {
LABEL_65:
      v87 = __dst.__index_; /*0x30f0*/
LABEL_70:
      memmove(v85, v87, (size_t)v81); /*0x3155*/
      goto LABEL_71; /*0x315b*/
    }
LABEL_69:
    v87 = (int *)((char *)&__dst.__loc_ + 1); /*0x314e*/
    goto LABEL_70; /*0x314e*/
  }
LABEL_71:
  strcpy((char *)v81 + (_QWORD)v85, "/libvdconn.dylib"); /*0x3160*/
  v90 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(
          &std::cout,
          "The full path of ./libvdconn.dylib is: ",
          39);
  if ( (__dst.__precision_ & 1) != 0 ) /*0x3194*/
  {
    v86 = *(char **)&__dst.__rdstate_; /*0x3196*/
    width = __dst.__width_; /*0x319d*/
  }
  else
  {
    width = LOBYTE(__dst.__precision_) >> 1; /*0x31a6*/
  }
  v92 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v90, v86, width); /*0x31b3*/
  std::ios_base::getloc(&__dst); /*0x31ca*/
  v93 = std::locale::use_facet((const std::locale *)&__dst, &std::ctype<char>::id); /*0x31d9*/
  v94 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v93->__vftable[2].~facet_0)(v93, 10); /*0x31ec*/
  std::locale::~locale((std::locale *)&__dst); /*0x31f2*/
  std::ostream::put(v92, (unsigned int)v94); /*0x31fe*/
  std::ostream::flush(v92); /*0x3206*/
  if ( (__dst.__precision_ & 1) != 0 ) /*0x3212*/
    operator delete(*(void **)&__dst.__rdstate_); /*0x321b*/
  if ( (loc_low & 1) != 0 ) /*0x3224*/
    operator delete(__dst.__index_); /*0x322d*/
LABEL_78:
  v95 = dlopen("libvdconn.dylib", 1); /*0x3232*/
  if ( !v95 )
  {
    v98 = dlerror(); /*0x328b*/
    printf("无法加载动态库: %s\n", v98);
    return __stack_chk_guard; /*0x32a1*/
  }
  v96 = v95; /*0x3248*/
  std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, "!!!!!!! ------- !!!!/n", 22); /*0x325e*/
  v97 = dlerror(); /*0x3263*/
  if ( !v97 )
  {
    std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, "xxxxxxxx\n", 9); /*0x32b9*/
    v99 = *((unsigned __int8 *)rdbuf + 104); /*0x32be*/
    if ( (v99 & 1) == 0 )
    {
      v100 = v99 & 0xFFFFFFFE; /*0x32c6*/
      if ( v100 != 14 )
      {
        v101 = *(_QWORD *)&__dst.__fmtflags_; /*0x32d5*/
        if ( v100 != 20 ) /*0x32dc*/
          goto LABEL_141; /*0x32dc*/
LABEL_89:
        if ( !(*(_QWORD *)v101 ^ 0x656E6E6F63736964LL | *(unsigned __int16 *)(v101 + 8) ^ 0x7463LL) )
        {
          v103 = (__int64 (__fastcall *)(char *, _QWORD (__fastcall *)(int, int, const char *, const char *)))dlsym(v96, "disconnectDesktop"); /*0x332a*/
          if ( !v103 ) /*0x3332*/
          {
            v113 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>( /*0x34d0*/
                     &std::cout,
                     "Get Func DisconnectDesktop Failed",
                     33);
            std::endl[abi:nn180100]<char,std::char_traits<char>>(v113); /*0x34d8*/
            return __stack_chk_guard; /*0x34dd*/
          }
          if ( (*((_BYTE *)rdbuf + 176) & 1) != 0 ) /*0x333f*/
            v104 = (char *)*((_QWORD *)rdbuf + 24); /*0x34fa*/
          else
            v104 = (char *)rdbuf + 177; /*0x3345*/
          v116 = v103(v104, disconnectCallback); /*0x350d*/
          v117 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(
                   &std::cout,
                   "disconnectDesktop ret val:  ",
                   28);
          v118 = std::ostream::operator<<(v117, v116); /*0x352c*/
          std::endl[abi:nn180100]<char,std::char_traits<char>>(v118); /*0x3534*/
        }
        goto LABEL_141; /*0x3539*/
      }
      if ( **(_DWORD **)&__dst.__fmtflags_ ^ 0x6E6E6F63 | *(_DWORD *)(*(_QWORD *)&__dst.__fmtflags_ + 3LL) ^ 0x7463656E ) /*0x339d*/
      {
        if ( **(_DWORD **)&__dst.__fmtflags_ ^ 0x74736572 /*0x33b0*/
           | *(_DWORD *)(*(_QWORD *)&__dst.__fmtflags_ + 3LL) ^ 0x74726174 )
        {
          goto LABEL_141; /*0x33b2*/
        }
        goto LABEL_101; /*0x33b2*/
      }
LABEL_104:
      v108 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>( /*0x3420*/
               &std::cout,
               "********************** do connect **********************/n",
               58);
      std::ios_base::getloc((const std::ios_base *)&__dst.__loc_); /*0x344f*/
      v109 = std::locale::use_facet((const std::locale *)&__dst.__loc_, &std::ctype<char>::id); /*0x345e*/
      v110 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v109->__vftable[2].~facet_0)(v109, 10); /*0x3471*/
      std::locale::~locale((std::locale *)&__dst.__loc_); /*0x3477*/
      std::ostream::put(v108, (unsigned int)v110); /*0x3483*/
      std::ostream::flush(v108); /*0x348b*/
      v111 = dlsym(v96, "connectDesktop"); /*0x349a*/
      if ( v111 )
      {
        if ( (*((_BYTE *)rdbuf + 128) & 1) != 0 ) /*0x34ab*/
          v112 = (char *)*((_QWORD *)rdbuf + 18); /*0x353e*/
        else
          v112 = (char *)rdbuf + 129; /*0x34b1*/
        if ( (*((_BYTE *)rdbuf + 152) & 1) != 0 ) /*0x354c*/
          v119 = (char *)*((_QWORD *)rdbuf + 21); /*0x3557*/
        else
          v119 = (char *)rdbuf + 153; /*0x354e*/
        if ( (*((_BYTE *)rdbuf + 176) & 1) != 0 ) /*0x3565*/
          v120 = (char *)*((_QWORD *)rdbuf + 24); /*0x3570*/
        else
          v120 = (char *)rdbuf + 177; /*0x3567*/
        if ( (*((_BYTE *)rdbuf + 200) & 1) != 0 ) /*0x357e*/
          v121 = (char *)*((_QWORD *)rdbuf + 27); /*0x3589*/
        else
          v121 = (char *)rdbuf + 201; /*0x3580*/
        if ( (*((_BYTE *)rdbuf + 232) & 1) != 0 ) /*0x359e*/
          v122 = (char *)*((_QWORD *)rdbuf + 31); /*0x35a9*/
        else
          v122 = (char *)rdbuf + 233; /*0x35a0*/
        v123 = ((__int64 (__fastcall *)(char *, char *, char *, char *, _QWORD, char *, _QWORD, _QWORD (__fastcall *)(int, int, const char *, const char *)))v111)( /*0x35c8*/
                 v112,
                 v119,
                 v120,
                 v121,
                 *((unsigned int *)rdbuf + 56),
                 v122,
                 *((unsigned int *)rdbuf + 64),
                 connectCallback);
        v124 = "connectDesktop ret val:  ";
        goto LABEL_140; /*0x35d8*/
      }
      v114 = "Get Func ConnectDesktop Failed"; /*0x34e9*/
      v115 = 30; /*0x34f0*/
LABEL_142:
      v133 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, v114, v115); /*0x3716*/
      std::ios_base::getloc((const std::ios_base *)&__dst.__loc_); /*0x3732*/
      v134 = std::locale::use_facet((const std::locale *)&__dst.__loc_, &std::ctype<char>::id); /*0x3741*/
      v135 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v134->__vftable[2].~facet_0)(v134, 10); /*0x3754*/
      std::locale::~locale((std::locale *)&__dst.__loc_); /*0x375a*/
      std::ostream::put(v133, (unsigned int)v135); /*0x3766*/
      std::ostream::flush(v133); /*0x376e*/
      return __stack_chk_guard; /*0x376e*/
    }
    v102 = *((_QWORD *)rdbuf + 14); /*0x32e3*/
    if ( v102 == 7 )
    {
      v105 = (_DWORD *)*((_QWORD *)rdbuf + 15); /*0x33c1*/
      if ( !(*v105 ^ 0x6E6E6F63 | *(_DWORD *)((char *)v105 + 3) ^ 0x7463656E) ) /*0x33d6*/
        goto LABEL_104; /*0x33d6*/
      if ( !(*v105 ^ 0x74736572 | *(_DWORD *)((char *)v105 + 3) ^ 0x74726174) )
      {
LABEL_101:
        v106 = dlsym(v96, "restartDesktop"); /*0x33ef*/
        if ( v106 )
        {
          if ( (*((_BYTE *)rdbuf + 128) & 1) != 0 ) /*0x340e*/
            v107 = (char *)*((_QWORD *)rdbuf + 18); /*0x35f5*/
          else
            v107 = (char *)rdbuf + 129; /*0x3414*/
          if ( (*((_BYTE *)rdbuf + 152) & 1) != 0 ) /*0x3603*/
            v125 = (char *)*((_QWORD *)rdbuf + 21); /*0x360e*/
          else
            v125 = (char *)rdbuf + 153; /*0x3605*/
          if ( (*((_BYTE *)rdbuf + 176) & 1) != 0 ) /*0x361c*/
            v126 = (char *)*((_QWORD *)rdbuf + 24); /*0x3627*/
          else
            v126 = (char *)rdbuf + 177; /*0x361e*/
          if ( (*((_BYTE *)rdbuf + 200) & 1) != 0 ) /*0x3635*/
            v127 = (char *)*((_QWORD *)rdbuf + 27); /*0x3640*/
          else
            v127 = (char *)rdbuf + 201; /*0x3637*/
          if ( (*((_BYTE *)rdbuf + 232) & 1) != 0 ) /*0x3655*/
            v128 = (char *)*((_QWORD *)rdbuf + 31); /*0x3660*/
          else
            v128 = (char *)rdbuf + 233; /*0x3657*/
          v123 = ((__int64 (__fastcall *)(char *, char *, char *, char *, _QWORD, char *, _QWORD, _QWORD (__fastcall *)(int, int, const char *, const char *)))v106)( /*0x367f*/
                   v107,
                   v125,
                   v126,
                   v127,
                   *((unsigned int *)rdbuf + 56),
                   v128,
                   *((unsigned int *)rdbuf + 64),
                   restartCallback);
          v124 = "restartDesktop ret val:  ";
LABEL_140:
          v129 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(&std::cout, v124, 25); /*0x368f*/
          v130 = std::ostream::operator<<(v129, v123); /*0x36a3*/
          std::ios_base::getloc((const std::ios_base *)&__dst.__loc_); /*0x36ba*/
          v131 = std::locale::use_facet((const std::locale *)&__dst.__loc_, &std::ctype<char>::id); /*0x36c9*/
          v132 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v131->__vftable[2].~facet_0)(v131, 10); /*0x36dc*/
          std::locale::~locale((std::locale *)&__dst.__loc_); /*0x36e2*/
          std::ostream::put(v130, (unsigned int)v132); /*0x36ee*/
          std::ostream::flush(v130); /*0x36f6*/
          goto LABEL_141; /*0x36f6*/
        }
        v114 = "Get Func RestartDesktop Failed"; /*0x35e4*/
        v115 = 30; /*0x35eb*/
        goto LABEL_142; /*0x35f0*/
      }
    }
    if ( v102 == 10 ) /*0x32f5*/
    {
      v101 = *((_QWORD *)rdbuf + 15); /*0x32fb*/
      goto LABEL_89; /*0x32fb*/
    }
LABEL_141:
    dlclose(v96); /*0x36fb*/
    v114 = "************** exit *****************"; /*0x370a*/
    v115 = 37; /*0x3711*/
    goto LABEL_142; /*0x3711*/
  }
  printf("无法加载动态库: %s\n", v97);
  dlclose(v96); /*0x3281*/
  return __stack_chk_guard; /*0x3783*/
}
