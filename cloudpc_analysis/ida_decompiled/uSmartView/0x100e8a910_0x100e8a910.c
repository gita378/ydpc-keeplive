// 0x100e8a910 @ 0x100e8a910
__int64 __fastcall sub_100E8A910(__int64 a1)
{
  __int64 type; // rax
  unsigned __int8 v2; // cl
  __int64 v3; // rdx
  __int64 v4; // r8
  __int64 v5; // r9
  unsigned __int8 v6; // cl
  int v7; // r9d
  unsigned __int8 v8; // cl
  unsigned __int8 v9; // cl
  unsigned __int8 i; // [rsp+17h] [rbp-19h]
  __int64 v12; // [rsp+18h] [rbp-18h]

  if ( a1 ) /*0x100e8a921*/
  {
    type = spice_session_get_type(); /*0x100e8a95c*/
    v12 = g_type_instance_get_private(a1, type); /*0x100e8a96d*/
    if ( v12 ) /*0x100e8a976*/
    {
      v2 = *(_BYTE *)(v12 + 5056); /*0x100e8a9ad*/
      *(_BYTE *)(v12 + 5056) = v2 + 1; /*0x100e8a9b8*/
      for ( i = v2; get_proxy_channel_manage_by_id(a1, i); i = v6 ) /*0x100e8a9be*/
      {
        v6 = *(_BYTE *)(v12 + 5056); /*0x100e8a9dc*/
        *(_BYTE *)(v12 + 5056) = v6 + 1; /*0x100e8a9e7*/
      }
      if ( !i ) /*0x100e8a9fd*/
      {
        if ( (unsigned int)spice_util_get_debug(a1, 0, v3, 0, v4, v5) && spice_gtk_log_level < 3 ) /*0x100e8aa20*/
          g_log( /*0x100e8aa48*/
            (unsigned int)"GSpice",
            16,
            (unsigned int)"[%-38s:%4d] vitrual link id 0 is invalid!",
            (unsigned int)"get_avaliable_virtual_channel_id",
            4641,
            v7);
        v8 = *(_BYTE *)(v12 + 5056); /*0x100e8aa56*/
        *(_BYTE *)(v12 + 5056) = v8 + 1; /*0x100e8aa61*/
        for ( i = v8; get_proxy_channel_manage_by_id(a1, i); i = v9 ) /*0x100e8aa67*/
        {
          v9 = *(_BYTE *)(v12 + 5056); /*0x100e8aa85*/
          *(_BYTE *)(v12 + 5056) = v9 + 1; /*0x100e8aa90*/
        }
      }
      return i; /*0x100e8aaa6*/
    }
    else
    {
      g_return_if_fail_warning("GSpice", "get_avaliable_virtual_channel_id", "s != NULL"); /*0x100e8a996*/
      return 0; /*0x100e8a99b*/
    }
  }
  else
  {
    g_return_if_fail_warning("GSpice", "get_avaliable_virtual_channel_id", "session != NULL"); /*0x100e8a941*/
    return 0; /*0x100e8a946*/
  }
}
