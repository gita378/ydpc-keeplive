// 0x61b0 @ 0x61b0
__int64 __fastcall create_http_tunnel_proxy(int a1, __int64 a2, int a3, __int64 a4, int a5)
{
  int v5; // r8d
  int v6; // r9d
  size_t v7; // rax
  int v8; // r8d
  int v9; // r9d
  int v10; // r8d
  int v11; // r9d
  int *v12; // rax
  int v13; // r8d
  int v14; // r9d
  int *v15; // rax
  int v16; // r9d
  int v18; // [rsp+3Ch] [rbp-1594h]
  timeval v19; // [rsp+40h] [rbp-1590h] BYREF
  fd_set v20; // [rsp+50h] [rbp-1580h] BYREF
  int v21; // [rsp+1050h] [rbp-580h]
  unsigned int v22; // [rsp+1054h] [rbp-57Ch]
  int v23; // [rsp+1058h] [rbp-578h]
  int v24; // [rsp+105Ch] [rbp-574h]
  __int64 v25; // [rsp+1060h] [rbp-570h]
  int v26; // [rsp+106Ch] [rbp-564h]
  __int64 v27; // [rsp+1070h] [rbp-560h]
  int v28; // [rsp+107Ch] [rbp-554h]
  fd_set *v29; // [rsp+1080h] [rbp-550h]
  int v30; // [rsp+108Ch] [rbp-544h]
  void *v31; // [rsp+1090h] [rbp-540h]
  int v32; // [rsp+1098h] [rbp-538h]
  int v33; // [rsp+109Ch] [rbp-534h]
  fd_set *v34; // [rsp+10A0h] [rbp-530h]
  int v35; // [rsp+10A8h] [rbp-528h]
  int v36; // [rsp+10ACh] [rbp-524h]
  void *v37; // [rsp+10B0h] [rbp-520h]
  int v38; // [rsp+10B8h] [rbp-518h]
  int v39; // [rsp+10BCh] [rbp-514h]
  char __big[1024]; // [rsp+10C0h] [rbp-510h] BYREF
  char __b[264]; // [rsp+14C0h] [rbp-110h] BYREF

  v28 = a1; /*0x61c9*/
  v27 = a2; /*0x61cf*/
  v26 = a3; /*0x61d6*/
  v25 = a4; /*0x61dc*/
  v24 = a5; /*0x61e3*/
  init_log(); /*0x61ea*/
  write_log( /*0x620a*/
    (unsigned int)"create_http_tunnel_proxy",
    1122,
    (unsigned int)"create_http_tunnel_proxy begin sock_fd %d",
    a1,
    v5,
    v6);
  v23 = 5; /*0x6218*/
  v22 = 0; /*0x6222*/
  memset(__b, 0, 0x100u); /*0x623f*/
  generate_http_msg(a2, v26, v25, (int)__b); /*0x625f*/
  v7 = strlen(__b); /*0x6289*/
  v21 = send(a1, __b, v7, 0); /*0x62a9*/
  if ( v21 > 0 ) /*0x62b6*/
  {
    __bzero(&v20, 4096); /*0x6301*/
    v30 = v28; /*0x630c*/
    v29 = &v20; /*0x6319*/
    v32 = v28; /*0x632d*/
    v31 = &v20; /*0x6333*/
    if ( &___darwin_check_fd_set_overflow ) /*0x6344*/
      v33 = __darwin_check_fd_set_overflow(v32, v31, 0); /*0x6363*/
    else
      v33 = 1; /*0x636e*/
    if ( v33 ) /*0x637f*/
      v29->fds_bits[(unsigned __int64)v30 >> 5] |= 1LL << (v30 & 0x1F); /*0x63b2*/
    v19.tv_sec = v23; /*0x63c2*/
    v19.tv_usec = 0; /*0x63c9*/
    memset(__big, 0, sizeof(__big)); /*0x63e9*/
    v18 = select_1050(v28 + 1, &v20, 0, 0, &v19); /*0x641a*/
    if ( v18 <= 0 ) /*0x6427*/
    {
      v15 = __error(); /*0x65b1*/
      write_log( /*0x65d4*/
        (unsigned int)"create_http_tunnel_proxy",
        1159,
        (unsigned int)"select failed! result=%d, errno=%d",
        v18,
        *v15,
        v16);
      v22 = -1; /*0x65d9*/
    }
    else
    {
      v35 = v28; /*0x6433*/
      v34 = &v20; /*0x6440*/
      v38 = v28; /*0x6454*/
      v37 = &v20; /*0x645a*/
      if ( &___darwin_check_fd_set_overflow ) /*0x646b*/
        v39 = __darwin_check_fd_set_overflow(v38, v37, 0); /*0x648a*/
      else
        v39 = 1; /*0x6495*/
      if ( v39 ) /*0x64a6*/
        v36 = (1LL << (v35 & 0x1F)) & v34->fds_bits[(unsigned __int64)v35 >> 5]; /*0x64db*/
      else
        v36 = 0; /*0x64e6*/
      if ( v36 ) /*0x64f7*/
      {
        if ( recv(v28, __big, 0x400u, 0) <= 0 ) /*0x651a*/
        {
          v12 = __error(); /*0x6570*/
          write_log( /*0x658c*/
            (unsigned int)"create_http_tunnel_proxy",
            1154,
            (unsigned int)"recv response failed  errno=%d !",
            *v12,
            v13,
            v14);
          v22 = -1; /*0x6591*/
        }
        else if ( !strstr(__big, "200 Connection established") ) /*0x652e*/
        {
          write_log( /*0x655c*/
            (unsigned int)"create_http_tunnel_proxy",
            1150,
            (unsigned int)"response is not 200 Connection established! and %s",
            (unsigned int)__big,
            v10,
            v11);
          v22 = -1; /*0x6561*/
        }
      }
    }
    write_log( /*0x65fe*/
      (unsigned int)"create_http_tunnel_proxy",
      1162,
      (unsigned int)"create_http_tunnel_proxy end sock_fd %d",
      v28,
      v10,
      v11);
  }
  else
  {
    write_log((unsigned int)"create_http_tunnel_proxy", 1132, (unsigned int)"msg send failed! result %d", v21, v8, v9); /*0x62d7*/
    return (unsigned int)-1; /*0x62dc*/
  }
  return v22; /*0x662c*/
}
