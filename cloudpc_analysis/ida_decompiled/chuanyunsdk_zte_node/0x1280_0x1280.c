// 0x1280 @ 0x1280
void __fastcall connectCallback(unsigned int a1, int a2, const char *a3, const char *a4)
{
  __int64 v5; // rbx
  const std::locale::facet *v6; // rax
  char v7; // r12
  __int64 v8; // rax
  __int64 v9; // rax
  __int64 v10; // rax
  __int64 v11; // rax
  __int64 v12; // rbx
  size_t v13; // rax
  __int64 v14; // rax
  __int64 v15; // rbx
  size_t v16; // rax
  __int64 v17; // rbx
  const std::locale::facet *v18; // rax
  char v19; // r12
  int iarray_high; // ebx
  const std::string::value_type *v21; // rsi
  const std::string::value_type *iarray_size; // r14
  __int64 v23; // rbx
  std::string *v24; // rdi
  __int64 v25; // rbx
  std::string *v26; // rdi
  std::ios_base v28; // [rsp+10h] [rbp-90h] BYREF

  LODWORD(v28.__iarray_size_) = a2; /*0x129b*/
  HIDWORD(v28.__iarray_) = a1; /*0x12a1*/
  v5 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>( /*0x12bc*/
         &std::cout,
         "****************  connectCallback",
         33);
  std::ios_base::getloc(&v28); /*0x12d3*/
  v6 = std::locale::use_facet((const std::locale *)&v28, &std::ctype<char>::id); /*0x12e2*/
  v7 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v6->__vftable[2].~facet_0)(v6, 10); /*0x12f5*/
  std::locale::~locale((std::locale *)&v28); /*0x12fb*/
  std::ostream::put(v5, (unsigned int)v7); /*0x1307*/
  std::ostream::flush(v5); /*0x130f*/
  v8 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(
         &std::cout,
         "connect callback function code: ",
         32);
  v9 = std::ostream::operator<<(v8, a1); /*0x1332*/
  v10 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v9, " iExtCode: ", 11);
  v11 = std::ostream::operator<<(v10, LODWORD(v28.__iarray_size_)); /*0x1358*/
  v12 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v11, " cMesg: ", 8);
  v13 = strlen(a3); /*0x1377*/
  v14 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v12, a3, v13); /*0x1385*/
  v15 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v14, " vmId : ", 8);
  v16 = strlen(a4); /*0x13a4*/
  v28.__iarray_size_ = (size_t)a4; /*0x13ac*/
  v17 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v15, a4, v16); /*0x13bb*/
  std::ios_base::getloc(&v28); /*0x13cb*/
  v18 = std::locale::use_facet((const std::locale *)&v28, &std::ctype<char>::id); /*0x13da*/
  v19 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v18->__vftable[2].~facet_0)(v18, 10); /*0x13ed*/
  std::locale::~locale((std::locale *)&v28); /*0x13f3*/
  std::ostream::put(v17, (unsigned int)v19); /*0x13ff*/
  std::ostream::flush(v17); /*0x1407*/
  memset(&v28.__fn_, 0, 24); /*0x1416*/
  memset(&v28, 0, 48); /*0x1422*/
  iarray_high = 0; /*0x1431*/
  if ( HIDWORD(v28.__iarray_) == 1 ) /*0x1436*/
  {
    v21 = "disconnect"; /*0x1448*/
  }
  else
  {
    v21 = "connect"; /*0x1438*/
    if ( HIDWORD(v28.__iarray_) != 2 ) /*0x1442*/
      iarray_high = HIDWORD(v28.__iarray_); /*0x1444*/
  }
  iarray_size = (const std::string::value_type *)v28.__iarray_size_; /*0x144f*/
  std::string::assign((std::string *)&v28, v21); /*0x145a*/
  std::string::assign((std::string *)&v28.__width_, iarray_size); /*0x1469*/
  LODWORD(v28.__loc_) = iarray_high; /*0x146e*/
  std::string::assign((std::string *)&v28.__fn_, a3); /*0x1477*/
  std::mutex::lock(&g_muxCallBackInfoLocker); /*0x1483*/
  v23 = *((_QWORD *)&g_vecCallBackInfo + 1); /*0x1488*/
  if ( *((_QWORD *)&g_vecCallBackInfo + 1) >= (unsigned __int64)qword_84A8 ) /*0x1496*/
  {
    v25 = std::vector<callBackInfo>::__push_back_slow_path<callBackInfo const&>(&g_vecCallBackInfo, &v28); /*0x14df*/
    goto LABEL_16; /*0x14e2*/
  }
  if ( ((__int64)v28.__vftable & 1) != 0 ) /*0x149f*/
  {
    std::string::__init_copy_ctor_external( /*0x14f2*/
      *((std::string **)&g_vecCallBackInfo + 1),
      (const std::string::value_type *)v28.__precision_,
      *(std::string::size_type *)&v28.__fmtflags_);
    v24 = (std::string *)(v23 + 24); /*0x14f7*/
    if ( (v28.__width_ & 1) != 0 ) /*0x14ff*/
      goto LABEL_8; /*0x14ff*/
LABEL_11:
    v24->__r_.__value_.__r.__words[2] = (std::string::size_type)v28.__rdbuf_; /*0x1501*/
    *(_OWORD *)&v24->__r_.__value_.__l.0 = *(_OWORD *)&v28.__width_; /*0x150d*/
    goto LABEL_12; /*0x150d*/
  }
  *(_QWORD *)(*((_QWORD *)&g_vecCallBackInfo + 1) + 16LL) = v28.__precision_; /*0x14a5*/
  *(_OWORD *)v23 = *(_OWORD *)&v28.__vftable; /*0x14b0*/
  v24 = (std::string *)(v23 + 24); /*0x14b3*/
  if ( (v28.__width_ & 1) == 0 ) /*0x14bb*/
    goto LABEL_11; /*0x14bb*/
LABEL_8:
  std::string::__init_copy_ctor_external( /*0x14bd*/
    v24,
    (const std::string::value_type *)v28.__rdbuf_,
    *(std::string::size_type *)&v28.__rdstate_);
LABEL_12:
  *(_DWORD *)(v23 + 48) = v28.__loc_; /*0x1510*/
  v26 = (std::string *)(v23 + 56); /*0x1516*/
  if ( ((__int64)v28.__fn_ & 1) != 0 ) /*0x151e*/
  {
    std::string::__init_copy_ctor_external( /*0x153b*/
      v26,
      (const std::string::value_type *)v28.__event_size_,
      (std::string::size_type)v28.__index_);
  }
  else
  {
    *(_QWORD *)(v23 + 72) = v28.__event_size_; /*0x1525*/
    *(_OWORD *)&v26->__r_.__value_.__l.0 = *(_OWORD *)&v28.__fn_; /*0x152e*/
  }
  v25 = v23 + 80; /*0x1540*/
LABEL_16:
  *((_QWORD *)&g_vecCallBackInfo + 1) = v25; /*0x1544*/
  std::mutex::unlock(&g_muxCallBackInfoLocker); /*0x1552*/
  if ( ((__int64)v28.__fn_ & 1) != 0 ) /*0x155b*/
  {
    operator delete((void *)v28.__event_size_); /*0x1588*/
    if ( (v28.__width_ & 1) == 0 ) /*0x1591*/
    {
LABEL_18:
      if ( ((__int64)v28.__vftable & 1) == 0 ) /*0x156a*/
        return; /*0x156a*/
      goto LABEL_19; /*0x156a*/
    }
  }
  else if ( (v28.__width_ & 1) == 0 ) /*0x1561*/
  {
    goto LABEL_18; /*0x1561*/
  }
  operator delete(v28.__rdbuf_); /*0x1597*/
  if ( ((__int64)v28.__vftable & 1) == 0 ) /*0x15a3*/
    return; /*0x15a3*/
LABEL_19:
  operator delete((void *)v28.__precision_); /*0x156c*/
}
