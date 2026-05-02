// 0x100e7b070 @ 0x100e7b070
__int64 __fastcall ikcp_get_syn_id(__int64 a1)
{
  int v2; // [rsp+68h] [rbp-1Ch] BYREF
  __int64 v3; // [rsp+6Ch] [rbp-18h]
  int *v4; // [rsp+74h] [rbp-10h]
  __int64 v5; // [rsp+7Ch] [rbp-8h]

  v3 = a1; /*0x100e7b075*/
  v5 = a1 + 11; /*0x100e7b092*/
  v4 = &v2; /*0x100e7b09a*/
  return *(unsigned int *)(a1 + 11); /*0x100e7b0bb*/
}
