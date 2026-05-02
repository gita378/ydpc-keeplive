// 0x1850 @ 0x1850
void __fastcall disconnectCallback(unsigned int a1, unsigned int a2, const char *a3, const char *a4)
{
  __int64 v6; // rax
  __int64 v7; // rax
  __int64 v8; // rax
  __int64 v9; // rax
  __int64 v10; // r12
  size_t v11; // rax
  __int64 v12; // rax
  __int64 v13; // r12
  size_t v14; // rax
  __int64 v15; // r12
  const std::locale::facet *v16; // rax
  char v17; // r14
  __int64 v18; // rbx
  std::string *v19; // rdi
  __int64 v20; // rbx
  std::string *v21; // rdi
  std::ios_base var80; // [rsp+0h] [rbp-80h] BYREF

  HIDWORD(var80.__event_cap_) = a1; /*0x186d*/
  v6 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(
         &std::cout,
         "disconnect callback function code: ",
         35);
  v7 = std::ostream::operator<<(v6, a1); /*0x188e*/
  v8 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v7, " iExtCode ", 10); /*0x18a2*/
  v9 = std::ostream::operator<<(v8, a2); /*0x18ad*/
  v10 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v9, " cMesg: ", 8);
  v11 = strlen(a3); /*0x18cc*/
  v12 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v10, a3, v11); /*0x18da*/
  v13 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v12, " vmId : ", 8);
  v14 = strlen(a4); /*0x18f9*/
  v15 = std::__put_character_sequence[abi:nn180100]<char,std::char_traits<char>>(v13, a4, v14); /*0x190c*/
  std::ios_base::getloc(&var80); /*0x1920*/
  v16 = std::locale::use_facet((const std::locale *)&var80, &std::ctype<char>::id); /*0x192f*/
  v17 = ((__int64 (__fastcall *)(const std::locale::facet *, __int64))v16->__vftable[2].~facet_0)(v16, 10); /*0x1942*/
  std::locale::~locale((std::locale *)&var80); /*0x1948*/
  std::ostream::put(v15, (unsigned int)v17); /*0x1954*/
  std::ostream::flush(v15); /*0x195c*/
  memset(&var80.__fn_, 0, 24); /*0x1968*/
  memset(&var80, 0, 48); /*0x1974*/
  std::string::assign((std::string *)&var80, "disconnect"); /*0x198b*/
  std::string::assign((std::string *)&var80.__width_, a4); /*0x199a*/
  LODWORD(var80.__loc_) = HIDWORD(var80.__event_cap_); /*0x19a2*/
  std::string::assign((std::string *)&var80.__fn_, a3); /*0x19ab*/
  std::mutex::lock(&g_muxCallBackInfoLocker); /*0x19b7*/
  v18 = *((_QWORD *)&g_vecCallBackInfo + 1); /*0x19bc*/
  if ( *((_QWORD *)&g_vecCallBackInfo + 1) >= (unsigned __int64)qword_84A8 ) /*0x19ca*/
  {
    v20 = std::vector<callBackInfo>::__push_back_slow_path<callBackInfo const&>(&g_vecCallBackInfo, &var80); /*0x1a0a*/
    goto LABEL_12; /*0x1a0d*/
  }
  if ( ((__int64)var80.__vftable & 1) != 0 ) /*0x19d0*/
  {
    std::string::__init_copy_ctor_external( /*0x1a1a*/
      *((std::string **)&g_vecCallBackInfo + 1),
      (const std::string::value_type *)var80.__precision_,
      *(std::string::size_type *)&var80.__fmtflags_);
    v19 = (std::string *)(v18 + 24); /*0x1a1f*/
    if ( (var80.__width_ & 1) != 0 ) /*0x1a27*/
      goto LABEL_4; /*0x1a27*/
LABEL_7:
    v19->__r_.__value_.__r.__words[2] = (std::string::size_type)var80.__rdbuf_; /*0x1a29*/
    *(_OWORD *)&v19->__r_.__value_.__l.0 = *(_OWORD *)&var80.__width_; /*0x1a36*/
    goto LABEL_8; /*0x1a36*/
  }
  *(_QWORD *)(*((_QWORD *)&g_vecCallBackInfo + 1) + 16LL) = var80.__precision_; /*0x19d6*/
  *(_OWORD *)v18 = *(_OWORD *)&var80.__vftable; /*0x19de*/
  v19 = (std::string *)(v18 + 24); /*0x19e1*/
  if ( (var80.__width_ & 1) == 0 ) /*0x19e9*/
    goto LABEL_7; /*0x19e9*/
LABEL_4:
  std::string::__init_copy_ctor_external( /*0x19eb*/
    v19,
    (const std::string::value_type *)var80.__rdbuf_,
    *(std::string::size_type *)&var80.__rdstate_);
LABEL_8:
  *(_DWORD *)(v18 + 48) = var80.__loc_; /*0x1a39*/
  v21 = (std::string *)(v18 + 56); /*0x1a3f*/
  if ( ((__int64)var80.__fn_ & 1) != 0 ) /*0x1a47*/
  {
    std::string::__init_copy_ctor_external( /*0x1a64*/
      v21,
      (const std::string::value_type *)var80.__event_size_,
      (std::string::size_type)var80.__index_);
  }
  else
  {
    *(_QWORD *)(v18 + 72) = var80.__event_size_; /*0x1a4e*/
    *(_OWORD *)&v21->__r_.__value_.__l.0 = *(_OWORD *)&var80.__fn_; /*0x1a57*/
  }
  v20 = v18 + 80; /*0x1a69*/
LABEL_12:
  *((_QWORD *)&g_vecCallBackInfo + 1) = v20; /*0x1a6d*/
  std::mutex::unlock(&g_muxCallBackInfoLocker); /*0x1a7b*/
  if ( ((__int64)var80.__fn_ & 1) != 0 ) /*0x1a84*/
  {
    operator delete((void *)var80.__event_size_); /*0x1aae*/
    if ( (var80.__width_ & 1) == 0 ) /*0x1ab7*/
    {
LABEL_14:
      if ( ((__int64)var80.__vftable & 1) == 0 ) /*0x1a90*/
        return; /*0x1a90*/
      goto LABEL_15; /*0x1a90*/
    }
  }
  else if ( (var80.__width_ & 1) == 0 ) /*0x1a8a*/
  {
    goto LABEL_14; /*0x1a8a*/
  }
  operator delete(var80.__rdbuf_); /*0x1abd*/
  if ( ((__int64)var80.__vftable & 1) == 0 ) /*0x1ac6*/
    return; /*0x1ac6*/
LABEL_15:
  operator delete((void *)var80.__precision_); /*0x1a92*/
}
