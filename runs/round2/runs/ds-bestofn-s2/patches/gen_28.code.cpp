FIT_UINT8 Field::GetNum(void) const
{
    const auto *p = profile;
    if (p == NULL)
        return FIT_FIELD_NUM_INVALID;
    const auto fields = p->fields;
    if (profileIndex >= p->numFields)
        return FIT_FIELD_NUM_INVALID;
    return fields[profileIndex].num;
}
