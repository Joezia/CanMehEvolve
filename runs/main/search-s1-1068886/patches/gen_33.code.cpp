
void FieldBase::SetUINT32Value(const FIT_UINT32 value, const FIT_UINT8 fieldArrayIndex)
{
    const size_t offset = fieldArrayIndex * sizeof(FIT_UINT32);
    if (values.size() < offset + sizeof(FIT_UINT32))
    {
        values.resize(offset + sizeof(FIT_UINT32));
    }
    std::memcpy(&values[offset], &value, sizeof(FIT_UINT32));
}
