
FIT_UINT8 Field::GetNum(void) const
{
    if (profile == NULL) return FIT_FIELD_NUM_INVALID;
    if (profileIndex >= profile->numFields) return FIT_FIELD_NUM_INVALID;
    return profile->fields[profileIndex].num;
}
