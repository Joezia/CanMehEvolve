
FIT_UINT8 Field::GetNum(void) const
{
    return (profile && profileIndex < profile->numFields)
        ? profile->fields[profileIndex].num
        : FIT_FIELD_NUM_INVALID;
}
