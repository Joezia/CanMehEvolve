```cpp
FIT_UINT8 Field::GetType() const
{
    if (type != FIT_UINT8_INVALID)
        return type;
    
    const FIT_FIELD_DEF* fields = profile ? profile->fields : nullptr;
    if (fields && (profileIndex < profile->numFields))
        return fields[profileIndex].type;
    
    return FIT_UINT8_INVALID;
}
