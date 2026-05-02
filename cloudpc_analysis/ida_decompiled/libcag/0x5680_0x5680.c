// 0x5680 @ 0x5680
__int64 __fastcall connect_to_access_gateway(unsigned int *a1)
{
  int v1; // r9d
  int v2; // r8d
  int v3; // r9d
  int v5; // [rsp+8h] [rbp-18h]
  int v6; // [rsp+Ch] [rbp-14h] BYREF
  int v7; // [rsp+10h] [rbp-10h] BYREF
  unsigned int v8; // [rsp+14h] [rbp-Ch]
  unsigned int *v9; // [rsp+18h] [rbp-8h]

  v9 = a1; /*0x5688*/
  v8 = 0; /*0x568c*/
  v7 = 0; /*0x5693*/
  v6 = 0; /*0x569a*/
  init_log(); /*0x56a8*/
  v5 = ZXRand(); /*0x56b2*/
  write_log( /*0x56d5*/
    (unsigned int)"connect_to_access_gateway",
    714,
    (unsigned int)"generate client key %u and random_key %u",
    v5,
    a1[21],
    v1);
  v8 = cag_param_valid_check(a1); /*0x56e5*/
  if ( !v8 ) /*0x56eb*/
  {
    v8 = send_access_gateway_local_key((__int64)v9, v5); /*0x5704*/
    if ( !v8 ) /*0x570a*/
    {
      v8 = recv_access_gateway_key(*v9, &v6, &v7, v9[21]); /*0x5731*/
      if ( !v8 ) /*0x5737*/
        return (unsigned int)send_access_gateway_connect_info(v9, v5, v6, v7, v2, v3); /*0x5754*/
    }
  }
  return v8; /*0x575a*/
}
