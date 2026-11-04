FIT_UINT8 Field::GetNum(void) const
{
    if ((profile == NULL) || (profileIndex >= profile->numFields))
        return FIT_FIELD_NUM_INVALID;
    return profile->fields[profileIndex].num;
}
