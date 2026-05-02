// 0x4c70 @ 0x4c70
__int64 __fastcall send_access_gateway_connect_info(unsigned int *a1, int a2, int a3, int a4, int a5, int a6)
{
  int v6; // eax
  int v7; // r8d
  int v8; // r9d
  int v9; // ecx
  int v10; // r8d
  int v11; // r9d
  int v12; // eax
  int v13; // r9d
  int v14; // r8d
  int v15; // r9d
  int v16; // eax
  int v17; // r8d
  int v18; // r9d
  int v19; // eax
  int v20; // ecx
  int v21; // r8d
  int v22; // r9d
  int v23; // ecx
  int v24; // r8d
  int v25; // r9d
  int v26; // r8d
  int v27; // r9d
  int v28; // r8d
  int v29; // r9d
  int v30; // eax
  int v31; // r8d
  int v32; // r9d
  int v33; // ecx
  int v34; // r8d
  int v35; // r9d
  int v36; // r8d
  int v37; // r9d
  int v38; // ecx
  int v39; // r8d
  int v40; // r9d
  int v41; // r8d
  int v42; // r9d
  int v43; // ecx
  int v44; // r8d
  int v45; // r9d
  int v46; // ecx
  int v47; // r8d
  int v48; // r9d
  int v50; // [rsp+78h] [rbp-1B8h]
  _DWORD v51[10]; // [rsp+98h] [rbp-198h] BYREF
  _WORD *v52; // [rsp+C0h] [rbp-170h]
  void *v53; // [rsp+C8h] [rbp-168h]
  signed int v54; // [rsp+D4h] [rbp-15Ch]
  void *v55; // [rsp+D8h] [rbp-158h]
  int sock_error; // [rsp+E0h] [rbp-150h]
  int v57; // [rsp+E4h] [rbp-14Ch]
  int v58; // [rsp+E8h] [rbp-148h]
  int v59; // [rsp+ECh] [rbp-144h]
  unsigned int *v60; // [rsp+F0h] [rbp-140h]
  _WORD v62[112]; // [rsp+100h] [rbp-130h] BYREF
  _BYTE __b[64]; // [rsp+1E0h] [rbp-50h] BYREF

  v60 = a1; /*0x4c8a*/
  v59 = a2; /*0x4c91*/
  v58 = a3; /*0x4c97*/
  v57 = a4; /*0x4c9d*/
  write_log( /*0x4cb8*/
    (unsigned int)"send_access_gateway_connect_info",
    923,
    (unsigned int)"start send connect info to cag...",
    a4,
    a5,
    a6);
  cag_dest_ip_print(a1); /*0x4cc4*/
  sock_error = 0; /*0x4ccb*/
  v55 = 0; /*0x4cd5*/
  memset(__b, 0, sizeof(__b)); /*0x4cec*/
  if ( *((_WORD *)a1 + 2) == 1 )
  {
    memset(v62, 0, 0xDCu); /*0x4d24*/
    v62[0] = *((_WORD *)v60 + 20); /*0x4d35*/
    ZXMemcpy(&v62[2], 16, v60 + 6, 16); /*0x4d69*/
    ZXMemcpy(&v62[10], 40, (char *)v60 + 42, 40); /*0x4d9b*/
    v62[94] |= *((unsigned __int8 *)v60 + 89); /*0x4db4*/
    v6 = ZXStrlen(v60 + 38, 64); /*0x4dd5*/
    write_log( /*0x4df1*/
      (unsigned int)"send_access_gateway_connect_info",
      934,
      (unsigned int)"start encrypt user name (len = %d)",
      v6,
      v7,
      v8);
    tn_deal_aes_code((__int64)(v60 + 38), 0x40u, (__int64)&v62[30], v59, v58, 0, v57); /*0x4e53*/
    write_log( /*0x4e6d*/
      (unsigned int)"send_access_gateway_connect_info",
      936,
      (unsigned int)"encrypt user name success",
      v9,
      v10,
      v11);
    if ( *((_WORD *)v60 + 108) && *((_QWORD *)v60 + 28) )
    {
      v50 = *((unsigned __int16 *)v60 + 108); /*0x4ebf*/
      v12 = ZXStrlen(*((_QWORD *)v60 + 28), 64); /*0x4ec5*/
      write_log( /*0x4ee8*/
        (unsigned int)"send_access_gateway_connect_info",
        939,
        (unsigned int)"start encrypt user password(len = %d)[%d]",
        v50,
        v12,
        v13);
      ZXSnprintf((unsigned int)__b, 64, (unsigned int)"%s", *((_QWORD *)v60 + 28), v14, v15); /*0x4f0d*/
      v16 = ZXStrlen(__b, 64); /*0x4f25*/
      xor_with_key(__b, v16, 99); /*0x4f39*/
      v55 = malloc(0x40u); /*0x4f4c*/
      if ( !v55 )
      {
        write_log(
          (unsigned int)"send_access_gateway_connect_info",
          944,
          (unsigned int)"ERROR: malloc failed",
          0,
          v17,
          v18);
        return 1002; /*0x4f84*/
      }
      ZXMemset(v55, 64, 0, 64); /*0x4f9d*/
      v19 = ZXStrlen(__b, 63); /*0x4fc9*/
      ZXMemcpy(v55, 63, __b, v19); /*0x4fe4*/
      tn_deal_aes_code((__int64)v55, 0x40u, (__int64)&v62[62], v59, v58, 0, v57); /*0x502e*/
      ZXMemset(__b, 64, 0, 64); /*0x5044*/
      ZXMemset(v55, 64, 0, 64); /*0x5060*/
      free(v55); /*0x5072*/
      write_log( /*0x508c*/
        (unsigned int)"send_access_gateway_connect_info",
        953,
        (unsigned int)"encrypt user password success",
        v20,
        v21,
        v22);
    }
    sock_error = send(*v60, v62, 0xDCu, 0); /*0x50b0*/
    goto LABEL_24; /*0x50b6*/
  }
  v54 = 0; /*0x50bb*/
  if ( *((_WORD *)v60 + 108) && *((_QWORD *)v60 + 28) )
  {
    v54 = *((unsigned __int16 *)v60 + 108) + 1; /*0x5102*/
    if ( v54 % 16 ) /*0x5114*/
      v54 = 16 * (v54 / 16 + 1); /*0x5133*/
    v55 = malloc(v54); /*0x5149*/
    if ( !v55 )
    {
      write_log(
        (unsigned int)"send_access_gateway_connect_info",
        967,
        (unsigned int)"ERROR: malloc failed",
        0,
        v26,
        v27);
      return 1002; /*0x5181*/
    }
    ZXMemset(v55, v54, 0, v54); /*0x519d*/
    ZXMemcpy(v55, v54, *((_QWORD *)v60 + 28), *((unsigned __int16 *)v60 + 108)); /*0x51d6*/
  }
  v53 = malloc(v54 + 126LL); /*0x51f4*/
  if ( v53 )
  {
    ZXMemset(v53, v54 + 126LL, 0, v54 + 126LL); /*0x5272*/
    v52 = v53; /*0x527e*/
    *((_WORD *)v53 + 62) = v54; /*0x5292*/
    *v52 = *((_WORD *)v60 + 20); /*0x52a8*/
    ZXMemcpy(v52 + 2, 16, v60 + 6, 16); /*0x52e6*/
    ZXMemcpy(v52 + 10, 40, (char *)v60 + 42, 40); /*0x5318*/
    v52[46] |= *((unsigned __int8 *)v60 + 89); /*0x5338*/
    v30 = ZXStrlen(v60 + 38, 64); /*0x5359*/
    write_log( /*0x5375*/
      (unsigned int)"send_access_gateway_connect_info",
      988,
      (unsigned int)"start encpty user name(len = %d)",
      v30,
      v31,
      v32);
    tn_deal_aes_code((__int64)(v60 + 38), 0x20u, (__int64)(v52 + 30), v59, v58, 0, v57); /*0x53d7*/
    write_log( /*0x53f1*/
      (unsigned int)"send_access_gateway_connect_info",
      990,
      (unsigned int)"encpty user name success",
      v33,
      v34,
      v35);
    if ( v55 ) /*0x53fe*/
    {
      write_log( /*0x541f*/
        (unsigned int)"send_access_gateway_connect_info",
        993,
        (unsigned int)"start encpty user password(len = %d)",
        v54,
        v36,
        v37);
      tn_deal_aes_code((__int64)v55, v54, (__int64)(v52 + 63), v59, v58, 0, v57); /*0x545a*/
      write_log( /*0x5474*/
        (unsigned int)"send_access_gateway_connect_info",
        995,
        (unsigned int)"encpty user password success",
        v38,
        v39,
        v40);
    }
    sock_error = send(*v60, v53, (unsigned __int16)v52[62] + 126LL, 0); /*0x54a6*/
    if ( v55 ) /*0x54b4*/
      free(v55); /*0x54c1*/
    free(v53); /*0x54cd*/
LABEL_24:
    if ( sock_error > 0 )
    {
      write_log( /*0x5530*/
        (unsigned int)"send_access_gateway_connect_info",
        1011,
        (unsigned int)"send connect info to cag success",
        v23,
        v24,
        v25);
      memset(v51, 0, 0x24u); /*0x5550*/
      if ( (int)receive_data_by_socket(*v60, v51, 36, v60[21]) == 36 )
      {
        write_log( /*0x55a4*/
          (unsigned int)"send_access_gateway_connect_info",
          1016,
          (unsigned int)"recv cag reply %d",
          v51[0],
          v44,
          v45);
        if ( v51[0] == 200 ) /*0x55b3*/
        {
          write_log( /*0x560d*/
            (unsigned int)"send_access_gateway_connect_info",
            1024,
            (unsigned int)"connect to cag success",
            v46,
            v47,
            v48);
          return 0; /*0x5612*/
        }
        else
        {
          return (unsigned int)v51[0]; /*0x55bf*/
        }
      }
      else
      {
        write_log(
          (unsigned int)"send_access_gateway_connect_info",
          1021,
          (unsigned int)"ERROR: connect to cag failed",
          v43,
          v44,
          v45);
        return (unsigned int)-1; /*0x55e9*/
      }
    }
    else
    {
      sock_error = get_sock_error(); /*0x54e4*/
      write_log(
        (unsigned int)"send_access_gateway_connect_info",
        1008,
        (unsigned int)"ERROR: send connect info to cag failed(%d)",
        sock_error,
        v41,
        v42);
      return (unsigned int)sock_error; /*0x5510*/
    }
  }
  write_log((unsigned int)"send_access_gateway_connect_info", 975, (unsigned int)"ERROR: malloc failed", 0, v28, v29);
  if ( v55 ) /*0x522a*/
    free(v55); /*0x5237*/
  return 1002; /*0x5645*/
}
