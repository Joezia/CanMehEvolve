FIT_UINT8 Field::GetType() const
{
    if (__builtin_expect(type != FIT_UINT8_INVALID, 0)) {
        return type;
    }
    if (__builtin_expect(profile != NULL && profileIndex < profile->numFields, 1)) {
        return profile->fields[profileIndex].type;
    }
    return type;
}
