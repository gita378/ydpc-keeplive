// 0x17220 @ 0x17220
void __fastcall ClientManager::StartSpiceProcess(__int64 a1, const std::string *a2, _DWORD *a3, unsigned int a4)
{
  _DWORD *v4; // r13
  std::string::__long::$5C0822F47C3855276CFDD0C01D0AA610 v6; // rdx
  std::string::pointer data; // r15
  signed __int64 size; // rdx
  std::string::pointer v9; // r14
  char *v10; // rbx
  void *v11; // rax
  char *v12; // rax
  std::string::__long::$5C0822F47C3855276CFDD0C01D0AA610 v13; // r14
  std::string::size_type v14; // r14
  size_t v15; // r14
  void *v16; // r13
  std::string::__long::$5C0822F47C3855276CFDD0C01D0AA610 v17; // rsi
  unsigned __int64 v18; // rsi
  int v19; // ebx
  std::__shared_weak_count *v20; // rbx
  size_t v21; // rax
  std::string::size_type v22; // r15
  char *v23; // r14
  size_t v24; // rbx
  __int64 v25; // r14
  __int64 v26; // r15
  _DWORD *v27; // r12
  const char *v28; // r15
  size_t v29; // rax
  std::string::size_type v30; // r13
  char *v31; // rbx
  __int64 v32; // r15
  _DWORD *v33; // r12
  const char *v34; // r15
  size_t v35; // rax
  std::string::size_type v36; // r13
  char *v37; // rbx
  std::string::value_type *v38; // rbx
  std::string::value_type *v39; // rbx
  size_t v40; // r14
  __int64 *v41; // rdi
  std::__shared_weak_count *v42; // rbx
  const char *v43; // r9
  std::__shared_weak_count *v44; // rbx
  size_t v45; // r14
  void *v46; // r13
  std::string::pointer v47; // rdx
  std::string::size_type v48; // rcx
  void (__fastcall *v49)(__int64, __int64, std::string *, __int64, _QWORD); // rbx
  std::__shared_weak_count *v50; // rbx
  const char *v51; // rbx
  const std::string::value_type *v52; // rsi
  std::string::size_type v53; // rdx
  std::__shared_weak_count *v54; // rbx
  std::__shared_weak_count *v55; // rbx
  char v56[8]; // [rsp+10h] [rbp-2A0h] BYREF
  std::__shared_weak_count *v57; // [rsp+18h] [rbp-298h]
  char v58[8]; // [rsp+20h] [rbp-290h] BYREF
  std::__shared_weak_count *v59; // [rsp+28h] [rbp-288h]
  char v60[8]; // [rsp+30h] [rbp-280h] BYREF
  std::__shared_weak_count *v61; // [rsp+38h] [rbp-278h]
  std::string v62; // [rsp+40h] [rbp-270h] BYREF
  std::string v63; // [rsp+58h] [rbp-258h] BYREF
  _DWORD *v64; // [rsp+70h] [rbp-240h]
  __int16 v65; // [rsp+78h] [rbp-238h] BYREF
  char v66; // [rsp+7Ah] [rbp-236h]
  void *v67; // [rsp+88h] [rbp-228h]
  __int16 v68; // [rsp+90h] [rbp-220h] BYREF
  char v69; // [rsp+92h] [rbp-21Eh]
  void *v70; // [rsp+A0h] [rbp-210h]
  __int16 v71; // [rsp+A8h] [rbp-208h] BYREF
  char v72; // [rsp+AAh] [rbp-206h]
  void *v73; // [rsp+B8h] [rbp-1F8h]
  char v74; // [rsp+C0h] [rbp-1F0h] BYREF
  int v75; // [rsp+C1h] [rbp-1EFh]
  void *v76; // [rsp+D0h] [rbp-1E0h]
  __int16 v77; // [rsp+D8h] [rbp-1D8h] BYREF
  char v78; // [rsp+DAh] [rbp-1D6h]
  void *v79; // [rsp+E8h] [rbp-1C8h]
  __int128 v80; // [rsp+F0h] [rbp-1C0h] BYREF
  void *v81; // [rsp+100h] [rbp-1B0h]
  __int64 v82; // [rsp+108h] [rbp-1A8h] BYREF
  std::__shared_weak_count *v83; // [rsp+110h] [rbp-1A0h]
  char v84; // [rsp+118h] [rbp-198h] BYREF
  char v85[15]; // [rsp+119h] [rbp-197h] BYREF
  void *v86; // [rsp+128h] [rbp-188h]
  char v87; // [rsp+130h] [rbp-180h] BYREF
  _BYTE v88[23]; // [rsp+131h] [rbp-17Fh] BYREF
  char v89; // [rsp+148h] [rbp-168h] BYREF
  _BYTE v90[23]; // [rsp+149h] [rbp-167h] BYREF
  char v91; // [rsp+160h] [rbp-150h] BYREF
  _BYTE v92[23]; // [rsp+161h] [rbp-14Fh] BYREF
  const void *v93; // [rsp+178h] [rbp-138h] BYREF
  const void *v94; // [rsp+180h] [rbp-130h] BYREF
  char v95; // [rsp+188h] [rbp-128h] BYREF
  char v96[15]; // [rsp+189h] [rbp-127h] BYREF
  void *__p; // [rsp+198h] [rbp-118h]
  std::string v98; // [rsp+1A0h] [rbp-110h] BYREF
  __int64 v99; // [rsp+1B8h] [rbp-F8h]
  __int64 v100; // [rsp+1C0h] [rbp-F0h] BYREF
  std::__shared_weak_count *v101; // [rsp+1C8h] [rbp-E8h]
  std::string v102; // [rsp+1D0h] [rbp-E0h] BYREF
  std::string __dst; // [rsp+1E8h] [rbp-C8h] BYREF
  unsigned int v104; // [rsp+204h] [rbp-ACh]
  std::thread v105; // [rsp+208h] [rbp-A8h] BYREF
  std::string __str; // [rsp+210h] [rbp-A0h] BYREF
  std::string v107; // [rsp+230h] [rbp-80h] BYREF
  std::string v108; // [rsp+250h] [rbp-60h] BYREF
  std::thread v109; // [rsp+268h] [rbp-48h] BYREF
  std::string v110; // [rsp+270h] [rbp-40h] BYREF

  v104 = a4; /*0x17234*/
  v4 = a3; /*0x1723a*/
  v99 = a1; /*0x17240*/
  CTraceManager::getVdnumKey(&v98, a3[1299]); /*0x17254*/
  *(_WORD *)&__str.__r_.__value_.__l.0 = 0; /*0x17259*/
  v6 = (std::string::__long::$5C0822F47C3855276CFDD0C01D0AA610)*(_BYTE *)&a2->__r_.__value_.__l.0; /*0x17262*/
  data = a2->__r_.__value_.__s.__data_; /*0x17267*/
  if ( (*(_BYTE *)&v6 & 1) != 0 ) /*0x1726f*/
  {
    size = a2->__r_.__value_.__l.__size_; /*0x17271*/
    v9 = a2->__r_.__value_.__l.__data_; /*0x17276*/
    if ( size <= 0 ) /*0x1727e*/
      goto LABEL_13; /*0x1727e*/
  }
  else
  {
    size = *(unsigned __int64 *)&v6 >> 1; /*0x17282*/
    v9 = a2->__r_.__value_.__s.__data_; /*0x17285*/
    if ( !size ) /*0x1728b*/
      goto LABEL_13; /*0x1728b*/
  }
  v10 = &v9[size]; /*0x1728d*/
  v11 = v9; /*0x17291*/
  do /*0x172a8*/
  {
    v12 = (char *)memchr(v11, 45, size); /*0x172a8*/
    if ( !v12 ) /*0x172b0*/
      break; /*0x172b0*/
    if ( *v12 == 45 ) /*0x172b5*/
    {
      if ( v12 != v10 && v12 - v9 != -1 ) /*0x172d3*/
      {
        std::string::operator=(&__str, a2); /*0x172df*/
        goto LABEL_33; /*0x172e4*/
      }
      break; /*0x172d3*/
    }
    v11 = v12 + 1; /*0x172b7*/
    size = v10 - (_BYTE *)v11; /*0x172bd*/
  }
  while ( v10 - (_BYTE *)v11 > 0 ); /*0x172a8*/
LABEL_13:
  write_log(0, 0, "StartSpiceProcess", 1458, "StartSpiceProcess test1"); /*0x172e9*/
  v13 = (std::string::__long::$5C0822F47C3855276CFDD0C01D0AA610)*(_BYTE *)&a2->__r_.__value_.__l.0; /*0x17307*/
  v64 = v4; /*0x17310*/
  if ( (*(_BYTE *)&v13 & 1) != 0 ) /*0x17317*/
    v14 = a2->__r_.__value_.__l.__size_; /*0x17319*/
  else
    v14 = *(unsigned __int64 *)&v13 >> 1; /*0x17320*/
  v15 = v14 + 1; /*0x17323*/
  v16 = operator new[](v15); /*0x1732e*/
  memset_s(v16, v15, 0, v15); /*0x1733c*/
  v17 = (std::string::__long::$5C0822F47C3855276CFDD0C01D0AA610)*(_BYTE *)&a2->__r_.__value_.__l.0; /*0x17341*/
  if ( (*(_BYTE *)&v17 & 1) != 0 ) /*0x1734a*/
  {
    data = a2->__r_.__value_.__l.__data_; /*0x1734c*/
    v18 = LODWORD(a2->__r_.__value_.__r.__words[1]); /*0x17351*/
  }
  else
  {
    v18 = *(unsigned __int64 *)&v17 >> 1; /*0x17358*/
  }
  v19 = AesDecodeConnStrFromCsap(data, v18, v16, (unsigned int)(v18 + 1)); /*0x17369*/
  write_log(0, 0, "StartSpiceProcess", 1468, "StartSpiceProcess AesDecodeConnStrFromCsap ret:%d", v19); /*0x17387*/
  if ( v19 ) /*0x1738e*/
  {
    CTraceManager::pop(v56, 2, &v98, 1); /*0x173a8*/
    v20 = v57; /*0x173ad*/
    if ( v57 && !_InterlockedExchangeAdd64(&v57->__shared_owners_, 0xFFFFFFFFFFFFFFFFLL) ) /*0x173c0*/
    {
      ((void (__fastcall *)(std::__shared_weak_count *))v20->__on_zero_shared)(v20); /*0x173d1*/
      std::__shared_weak_count::__release_weak(v20); /*0x173d7*/
    }
    operator delete[](v16); /*0x173df*/
    goto LABEL_140; /*0x173e4*/
  }
  v21 = strlen((const char *)v16); /*0x173ec*/
  if ( v21 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x173f5*/
    std::string::__throw_length_error[abi:v15006](&__dst); /*0x180ae*/
  v22 = v21; /*0x173fb*/
  if ( v21 >= 0x17 ) /*0x17402*/
  {
    v24 = (v21 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x17423*/
    v23 = (char *)operator new(v24); /*0x1742f*/
    __dst.__r_.__value_.__r.__words[2] = (std::string::size_type)v23; /*0x17432*/
    __dst.__r_.__value_.__r.__words[0] = v24 | 1; /*0x1743d*/
    __dst.__r_.__value_.__l.__size_ = v22; /*0x17444*/
  }
  else
  {
    __dst.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)(2 * v21); /*0x17408*/
    v23 = __dst.__r_.__value_.__s.__data_; /*0x1740e*/
    if ( !v21 ) /*0x17418*/
      goto LABEL_30; /*0x17418*/
  }
  memcpy(v23, v16, v22); /*0x17454*/
LABEL_30:
  v23[v22] = 0; /*0x17459*/
  if ( (*(_BYTE *)&__str.__r_.__value_.__s.0 & 1) != 0 ) /*0x17465*/
    operator delete(__str.__r_.__value_.__l.__data_); /*0x1746e*/
  __str = __dst; /*0x1747a*/
  operator delete[](v16); /*0x17492*/
  v4 = v64; /*0x17497*/
LABEL_33:
  *(_WORD *)&__dst.__r_.__value_.__l.0 = 0; /*0x1749e*/
  UrlDecode(&__str, &__dst); /*0x174b5*/
  v25 = v99; /*0x174ba*/
  std::string::operator=(&__str, &__dst); /*0x174cf*/
  if ( !(unsigned __int8)ClientManager::AddConnectParm(v25, &__str, v4, v104) )
  {
    v110.__r_.__value_.__r.__words[2] = (std::string::size_type)operator new(0x60u); /*0x1759d*/
    *(_OWORD *)&v110.__r_.__value_.__l.0 = xmmword_2073C0; /*0x175a8*/
    strcpy(
      v110.__r_.__value_.__l.__data_,
      "Failed to connect to desktop, please click to connect to desktop again [Error code: 20042]");
    GetLanguageType(); /*0x175f5*/
    if ( !std::string::compare(&v107, "zh") ) /*0x17605*/
      std::string::assign(&v110, "连接桌面失败，请重新点击连接桌面【错误码：20042】"); /*0x17619*/
    v108.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)18; /*0x1761e*/
    strcpy(v108.__r_.__value_.__s.__data_, "start_vdi"); /*0x1762c*/
    CTraceManager::addName(&v102, 2, 22, &v98, &v108, (unsigned int)v4[1299]); /*0x17659*/
    if ( (*(_BYTE *)&v108.__r_.__value_.__s.0 & 1) != 0 ) /*0x17662*/
      operator delete(v108.__r_.__value_.__l.__data_); /*0x17668*/
    v32 = *(_QWORD *)(v25 + 3960); /*0x1766d*/
    if ( !v32 ) /*0x17677*/
    {
      v108.__r_.__value_.__s.0 = 0; /*0x176c3*/
      v39 = v108.__r_.__value_.__s.__data_; /*0x176c7*/
LABEL_94:
      *v39 = 0; /*0x17b62*/
      CTraceManager::setUserNo(&v102, &v108); /*0x17b70*/
      if ( (*(_BYTE *)&v108.__r_.__value_.__s.0 & 1) != 0 ) /*0x17b79*/
        operator delete(v108.__r_.__value_.__l.__data_); /*0x17b7f*/
      CTraceManager::setVmid(&v102, v4 + 1654); /*0x17b92*/
      *(_WORD *)&v108.__r_.__value_.__l.0 = 0; /*0x17b97*/
      CTraceManager::setError(&v102, 20014, &v110, &v108); /*0x17bb1*/
      if ( (*(_BYTE *)&v108.__r_.__value_.__s.0 & 1) != 0 ) /*0x17bba*/
        operator delete(v108.__r_.__value_.__l.__data_); /*0x17bc0*/
      CTraceManager::upload(&v102); /*0x17bcc*/
      *v4 = 20014; /*0x17bd1*/
      v46 = v4 + 3; /*0x17bd9*/
      if ( (*(_BYTE *)&v110.__r_.__value_.__s.0 & 1) != 0 ) /*0x17be4*/
      {
        v47 = v110.__r_.__value_.__l.__data_; /*0x17be6*/
        v48 = v110.__r_.__value_.__l.__size_; /*0x17bea*/
      }
      else
      {
        v48 = (unsigned __int64)*(_BYTE *)&v110.__r_.__value_.__l.0 >> 1; /*0x17bf0*/
        v47 = v110.__r_.__value_.__s.__data_; /*0x17bf3*/
      }
      ZXMemcpy(v46, 0x400u, v47, v48); /*0x17bff*/
      v49 = *(void (__fastcall **)(__int64, __int64, std::string *, __int64, _QWORD))((char *)&loc_18818 + v25); /*0x17c04*/
      std::string::basic_string(&v62, &v110); /*0x17c16*/
      v49(1, 20014, &v62, 5, *(unsigned int *)(v25 + 23528)); /*0x17c38*/
      if ( (*(_BYTE *)&v62.__r_.__value_.__s.0 & 1) != 0 ) /*0x17c41*/
        operator delete(v62.__r_.__value_.__l.__data_); /*0x17c4a*/
      v50 = (std::__shared_weak_count *)v102.__r_.__value_.__l.__size_; /*0x17c4f*/
      if ( v102.__r_.__value_.__l.__size_ /*0x17c62*/
        && !_InterlockedExchangeAdd64(
              (volatile signed __int64 *)(v102.__r_.__value_.__l.__size_ + 8),
              0xFFFFFFFFFFFFFFFFLL) )
      {
        ((void (__fastcall *)(std::__shared_weak_count *))v50->__on_zero_shared)(v50); /*0x17c73*/
        std::__shared_weak_count::__release_weak(v50); /*0x17c79*/
      }
      if ( (*(_BYTE *)&v107.__r_.__value_.__s.0 & 1) != 0 ) /*0x17c82*/
        operator delete(v107.__r_.__value_.__l.__data_); /*0x17c88*/
      if ( (*(_BYTE *)&v110.__r_.__value_.__s.0 & 1) != 0 ) /*0x17c91*/
        operator delete(v110.__r_.__value_.__l.__data_); /*0x17c9b*/
      goto LABEL_138; /*0x17ca0*/
    }
    v33 = v4; /*0x17679*/
    v34 = (const char *)(v32 + 4); /*0x1767c*/
    v35 = strlen(v34); /*0x17683*/
    if ( v35 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x1768c*/
      std::string::__throw_length_error[abi:v15006](&v108); /*0x180c4*/
    v36 = v35; /*0x17692*/
    if ( v35 >= 0x17 ) /*0x17699*/
    {
      v45 = (v35 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x17b28*/
      v37 = (char *)operator new(v45); /*0x17b34*/
      v108.__r_.__value_.__r.__words[2] = (std::string::size_type)v37; /*0x17b37*/
      v108.__r_.__value_.__r.__words[0] = v45 | 1; /*0x17b3f*/
      v108.__r_.__value_.__l.__size_ = v36; /*0x17b43*/
      v25 = v99; /*0x17b47*/
    }
    else
    {
      v108.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)(2 * v35); /*0x176a4*/
      v37 = v108.__r_.__value_.__s.__data_; /*0x176a7*/
      if ( !v35 ) /*0x176ae*/
        goto LABEL_93; /*0x176ae*/
    }
    memmove(v37, v34, v36); /*0x17b57*/
LABEL_93:
    v39 = &v37[v36]; /*0x17b5c*/
    v4 = v33; /*0x17b5f*/
    goto LABEL_94; /*0x17b5f*/
  }
  v110.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)18; /*0x174f4*/
  strcpy(v110.__r_.__value_.__s.__data_, "start_vdi"); /*0x17502*/
  CTraceManager::addName(&v100, 2, 22, &v98, &v110, (unsigned int)v4[1299]); /*0x1752f*/
  if ( (*(_BYTE *)&v110.__r_.__value_.__s.0 & 1) != 0 ) /*0x17538*/
    operator delete(v110.__r_.__value_.__l.__data_); /*0x1753e*/
  v26 = *(_QWORD *)(v25 + 3960); /*0x17543*/
  if ( !v26 ) /*0x1754d*/
  {
    v110.__r_.__value_.__s.0 = 0; /*0x176b9*/
    v38 = v110.__r_.__value_.__s.__data_; /*0x176bd*/
    goto LABEL_55; /*0x176c1*/
  }
  v27 = v4; /*0x17553*/
  v28 = (const char *)(v26 + 4); /*0x17556*/
  v29 = strlen(v28); /*0x1755d*/
  if ( v29 >= 0xFFFFFFFFFFFFFFF0LL ) /*0x17566*/
    std::string::__throw_length_error[abi:v15006](&v110); /*0x180b9*/
  v30 = v29; /*0x1756c*/
  if ( v29 >= 0x17 ) /*0x17573*/
  {
    v40 = (v29 + 16) & 0xFFFFFFFFFFFFFFF0LL; /*0x176d4*/
    v31 = (char *)operator new(v40); /*0x176e0*/
    v110.__r_.__value_.__r.__words[2] = (std::string::size_type)v31; /*0x176e3*/
    v110.__r_.__value_.__r.__words[0] = v40 | 1; /*0x176eb*/
    v110.__r_.__value_.__l.__size_ = v30; /*0x176ef*/
    v25 = v99; /*0x176f3*/
  }
  else
  {
    v110.__r_.__value_.__s.0 = (std::string::__short::$7162EEB0FEF29CC674EFA33D0008C7E0)(2 * v29); /*0x1757e*/
    v31 = v110.__r_.__value_.__s.__data_; /*0x17581*/
    if ( !v29 ) /*0x17588*/
      goto LABEL_54; /*0x17588*/
  }
  memmove(v31, v28, v30); /*0x17703*/
LABEL_54:
  v38 = &v31[v30]; /*0x17708*/
  v4 = v27; /*0x1770b*/
LABEL_55:
  *v38 = 0; /*0x1770e*/
  CTraceManager::setUserNo(&v100, &v110); /*0x1771c*/
  if ( (*(_BYTE *)&v110.__r_.__value_.__s.0 & 1) != 0 ) /*0x17725*/
    operator delete(v110.__r_.__value_.__l.__data_); /*0x1772b*/
  v41 = &v100; /*0x17737*/
  CTraceManager::setVmid(&v100, v4 + 1654); /*0x1773e*/
  v82 = v100; /*0x17751*/
  v83 = v101; /*0x17758*/
  if ( v101 ) /*0x17762*/
    _InterlockedIncrement64(&v101->__shared_owners_); /*0x17764*/
  ClientManager::AddTraceParm(&v100, &v82, &__str); /*0x17777*/
  v42 = v83; /*0x1777c*/
  if ( v83 && !_InterlockedExchangeAdd64(&v83->__shared_owners_, 0xFFFFFFFFFFFFFFFFLL) ) /*0x1778f*/
  {
    ((void (__fastcall *)(std::__shared_weak_count *))v42->__on_zero_shared)(v42); /*0x177a0*/
    v41 = (__int64 *)v42; /*0x177a3*/
    std::__shared_weak_count::__release_weak(v42); /*0x177a6*/
  }
  ClientManager::AddFileTransferParm(v41, &__str); /*0x177b2*/
  ClientManager::SetPrinterPath(v41, &__str, v4); /*0x177c1*/
  ClientManager::SetDfsDataAndConfig(v25, &__str, v4); /*0x177d3*/
  ClientManager::SetPersonalizedConfig(v25, &__str, v4); /*0x177e2*/
  std::string::basic_string(&v63, &__str); /*0x177f5*/
  ClientManager::SetDCAndOsTypeToConfig(v25, &v63, v4); /*0x17807*/
  if ( (*(_BYTE *)&v63.__r_.__value_.__s.0 & 1) != 0 ) /*0x17813*/
    operator delete(v63.__r_.__value_.__l.__data_); /*0x1781c*/
  std::string::basic_string(&v110, &__str); /*0x1782c*/
  v87 = 24; /*0x17831*/
  strcpy(v88, "--guest-usr "); /*0x17842*/
  v65 = 8194; /*0x1785a*/
  v66 = 0; /*0x17863*/
  DeleteSerectInfoForLog(&v110, &v87, &v65); /*0x1787c*/
  if ( (v65 & 1) != 0 ) /*0x17888*/
    operator delete(v67); /*0x17891*/
  if ( (v87 & 1) != 0 ) /*0x1789d*/
    operator delete(*(void **)&v88[15]); /*0x178a6*/
  v89 = 30; /*0x178ab*/
  strcpy(v90, "--guest-passwd "); /*0x178b2*/
  v68 = 8194; /*0x178d1*/
  v69 = 0; /*0x178da*/
  DeleteSerectInfoForLog(&v110, &v89, &v68); /*0x178f3*/
  if ( (v68 & 1) != 0 ) /*0x178ff*/
    operator delete(v70); /*0x17908*/
  if ( (v89 & 1) != 0 ) /*0x17914*/
    operator delete(*(void **)&v90[15]); /*0x1791d*/
  v91 = 28; /*0x17922*/
  strcpy(v92, "--accessToken "); /*0x17933*/
  v71 = 8194; /*0x17952*/
  v72 = 0; /*0x1795b*/
  DeleteSerectInfoForLog(&v110, &v91, &v71); /*0x17974*/
  if ( (v71 & 1) != 0 ) /*0x17980*/
    operator delete(v73); /*0x17989*/
  if ( (v91 & 1) != 0 ) /*0x17995*/
    operator delete(*(void **)&v92[15]); /*0x1799e*/
  v74 = 6; /*0x179a3*/
  v75 = 2124589; /*0x179aa*/
  v77 = 8194; /*0x179b4*/
  v78 = 0; /*0x179bd*/
  DeleteSerectInfoForLog(&v110, &v74, &v77); /*0x179d6*/
  if ( (v77 & 1) != 0 ) /*0x179e2*/
    operator delete(v79); /*0x179eb*/
  if ( (v74 & 1) != 0 ) /*0x179f7*/
    operator delete(v76); /*0x17a00*/
  *(_WORD *)&v107.__r_.__value_.__l.0 = 0; /*0x17a05*/
  CTraceManager::setParams(&v100, &v110, &v107); /*0x17a1a*/
  if ( (*(_BYTE *)&v107.__r_.__value_.__s.0 & 1) != 0 ) /*0x17a23*/
    operator delete(v107.__r_.__value_.__l.__data_); /*0x17a29*/
  CTraceManager::upload(&v100); /*0x17a35*/
  if ( (*(_BYTE *)&v110.__r_.__value_.__s.0 & 1) != 0 ) /*0x17a3e*/
    v43 = v110.__r_.__value_.__l.__data_; /*0x17a40*/
  else
    v43 = v110.__r_.__value_.__s.__data_; /*0x17a46*/
  write_log(0, 0, "StartSpiceProcess", 1522, "StartSpiceProcess AddConnectParm cmd:%s", v43); /*0x17a63*/
  if ( (v4[1300] | 2) == 3 ) /*0x17a75*/
  {
    ClientManager::AddVappParam(v25, &__str, v4, v104); /*0x17a8e*/
    ClientManager::IsOpenRundll(v25, &__str); /*0x17a9d*/
    CTraceManager::pop(v58, 2, &v98, 1); /*0x17aba*/
    v44 = v59; /*0x17abf*/
    if ( v59 && !_InterlockedExchangeAdd64(&v59->__shared_owners_, 0xFFFFFFFFFFFFFFFFLL) ) /*0x17ad6*/
    {
      ((void (__fastcall *)(std::__shared_weak_count *))v44->__on_zero_shared)(v44); /*0x17aeb*/
      std::__shared_weak_count::__release_weak(v44); /*0x17af1*/
    }
    goto LABEL_133; /*0x17af6*/
  }
  if ( !getenv("APP_SANDBOX_CONTAINER_ID") ) /*0x17b0a*/
  {
    memset(&v107, 0, sizeof(v107)); /*0x17ca8*/
    v93 = 0; /*0x17cb4*/
    v94 = 0; /*0x17cbf*/
    ClientManager::ConnectStrWriteShareMemory("APP_SANDBOX_CONTAINER_ID", &__str, &v107, &v93, &v94); /*0x17ce3*/
    write_log(1, 0, "StartSpiceProcess", 1555, "handle:%p buf:%p", v93, v94); /*0x17d16*/
    v108.__r_.__value_.__r.__words[2] = (std::string::size_type)operator new(0x20u); /*0x17d25*/
    *(_OWORD *)&v108.__r_.__value_.__l.0 = xmmword_2073D0; /*0x17d30*/
    strcpy(v108.__r_.__value_.__l.__data_, "./uSmartView_VDI_Client --vmid "); /*0x17d46*/
    v51 = v107.__r_.__value_.__s.__data_; /*0x17d51*/
    if ( (*(_BYTE *)&v107.__r_.__value_.__s.0 & 1) != 0 ) /*0x17d58*/
    {
      v52 = v107.__r_.__value_.__l.__data_; /*0x17d5a*/
      v53 = v107.__r_.__value_.__l.__size_; /*0x17d5e*/
    }
    else
    {
      v53 = (unsigned __int64)*(_BYTE *)&v107.__r_.__value_.__l.0 >> 1; /*0x17d64*/
      v52 = v107.__r_.__value_.__s.__data_; /*0x17d67*/
    }
    std::string::append(&v108, v52, v53); /*0x17d6e*/
    std::string::append(&v108, " &"); /*0x17d7e*/
    if ( (*(_BYTE *)&v107.__r_.__value_.__s.0 & 1) != 0 ) /*0x17d87*/
      v51 = v107.__r_.__value_.__l.__data_; /*0x17d89*/
    write_log(1, 0, "StartSpiceProcess", 1588, "--vmid %s", v51); /*0x17dac*/
    *(_WORD *)&v102.__r_.__value_.__l.0 = 0; /*0x17db1*/
    v95 = 12; /*0x17dba*/
    strcpy(v96, "Server"); /*0x17dc1*/
    v84 = 8; /*0x17ddb*/
    strcpy(v85, "Type"); /*0x17de2*/
    v81 = operator new(0x20u); /*0x17dfd*/
    v80 = xmmword_2073E0; /*0x17e0b*/
    strcpy((char *)v81, "../config/installinfo.ini"); /*0x17e24*/
    ReadStringFromConfigFile(&v95, &v84, &v102, &v80, 0, 1); /*0x17e50*/
    if ( (v80 & 1) != 0 ) /*0x17e5c*/
    {
      operator delete(v81); /*0x17ec9*/
      if ( (v84 & 1) == 0 ) /*0x17ed5*/
      {
LABEL_117:
        if ( (v95 & 1) == 0 ) /*0x17e6e*/
          goto LABEL_119; /*0x17e6e*/
        goto LABEL_118; /*0x17e6e*/
      }
    }
    else if ( (v84 & 1) == 0 ) /*0x17e65*/
    {
      goto LABEL_117; /*0x17e65*/
    }
    operator delete(v86); /*0x17ede*/
    if ( (v95 & 1) == 0 ) /*0x17eea*/
    {
LABEL_119:
      v105.__t_ = 0; /*0x17e7c*/
      if ( !std::string::compare(&v102, "soho") ) /*0x17e9c*/
        std::thread::thread<void (&)(std::string const&,std::string const&,std::string const&),char const(&)[33],char const(&)[7],std::string&,void>( /*0x17f0b*/
          &v109,
          fork2StartVdi,
          "./../MacOS/uSmartView_VDI_Client",
          "--vmid",
          &v107);
      else
        std::thread::thread<void (&)(std::string const&,std::string const&,std::string const&),char const(&)[72],char const(&)[7],std::string&,void>( /*0x17ebb*/
          &v109,
          fork2StartVdi,
          "./../bin/uSmartView_VDI_Client.app/Contents/MacOS/uSmartView_VDI_Client",
          "--vmid",
          &v107);
      if ( v105.__t_ ) /*0x17f18*/
        std::terminate(); /*0x180cb*/
      v105.__t_ = v109.__t_; /*0x17f22*/
      v109.__t_ = 0; /*0x17f29*/
      std::thread::~thread(&v109); /*0x17f35*/
      std::thread::detach(&v105); /*0x17f41*/
      std::thread::thread<void (&)(std::string),std::string&,void>(&v109.__t_); /*0x17f55*/
      std::thread::detach(&v109); /*0x17f5e*/
      CTraceManager::pop(v60, 2, &v98, 1); /*0x17f7b*/
      v54 = v61; /*0x17f80*/
      if ( v61 && !_InterlockedExchangeAdd64(&v61->__shared_owners_, 0xFFFFFFFFFFFFFFFFLL) ) /*0x17f93*/
      {
        ((void (__fastcall *)(std::__shared_weak_count *))v54->__on_zero_shared)(v54); /*0x17fa4*/
        std::__shared_weak_count::__release_weak(v54); /*0x17faa*/
      }
      std::thread::~thread(&v109); /*0x17fb3*/
      std::thread::~thread(&v105); /*0x17fbf*/
      if ( (*(_BYTE *)&v102.__r_.__value_.__s.0 & 1) != 0 ) /*0x17fcb*/
      {
        operator delete(v102.__r_.__value_.__l.__data_); /*0x18080*/
        if ( (*(_BYTE *)&v108.__r_.__value_.__s.0 & 1) == 0 ) /*0x18089*/
        {
LABEL_131:
          if ( (*(_BYTE *)&v107.__r_.__value_.__s.0 & 1) == 0 ) /*0x17fdf*/
            goto LABEL_133; /*0x17fdf*/
LABEL_132:
          operator delete(v107.__r_.__value_.__l.__data_); /*0x17fe1*/
          goto LABEL_133; /*0x17fe5*/
        }
      }
      else if ( (*(_BYTE *)&v108.__r_.__value_.__s.0 & 1) == 0 ) /*0x17fd5*/
      {
        goto LABEL_131; /*0x17fd5*/
      }
      operator delete(v108.__r_.__value_.__l.__data_); /*0x18093*/
      if ( (*(_BYTE *)&v107.__r_.__value_.__s.0 & 1) == 0 ) /*0x1809c*/
        goto LABEL_133; /*0x1809c*/
      goto LABEL_132; /*0x1809c*/
    }
LABEL_118:
    operator delete(__p); /*0x17e70*/
    goto LABEL_119; /*0x17e77*/
  }
  ClientManager::StartSpiceProcessinSandBox(v25, &__str); /*0x17b1a*/
LABEL_133:
  if ( (*(_BYTE *)&v110.__r_.__value_.__s.0 & 1) != 0 ) /*0x17fee*/
    operator delete(v110.__r_.__value_.__l.__data_); /*0x17ff4*/
  v55 = v101; /*0x17ff9*/
  if ( v101 && !_InterlockedExchangeAdd64(&v101->__shared_owners_, 0xFFFFFFFFFFFFFFFFLL) ) /*0x1800c*/
  {
    ((void (__fastcall *)(std::__shared_weak_count *))v55->__on_zero_shared)(v55); /*0x1801d*/
    std::__shared_weak_count::__release_weak(v55); /*0x18023*/
  }
LABEL_138:
  if ( (*(_BYTE *)&__dst.__r_.__value_.__s.0 & 1) != 0 ) /*0x1802f*/
    operator delete(__dst.__r_.__value_.__l.__data_); /*0x18038*/
LABEL_140:
  if ( (*(_BYTE *)&__str.__r_.__value_.__s.0 & 1) != 0 ) /*0x18044*/
    operator delete(__str.__r_.__value_.__l.__data_); /*0x1804d*/
  if ( (*(_BYTE *)&v98.__r_.__value_.__s.0 & 1) != 0 ) /*0x18059*/
    operator delete(v98.__r_.__value_.__l.__data_); /*0x18062*/
}
