
Field::Field(const FIT_UINT16 mesgNum, const FIT_UINT8 fieldNum)
    : FieldBase()
    , profile(Profile::GetMesg(mesgNum))
    , profileIndex(Profile::GetFieldIndex(mesgNum, fieldNum))
    , type(static_cast<FIT_UINT8>(0xFF))
    , isFieldExpanded(static_cast<FIT_BOOL>(0))
{
}
