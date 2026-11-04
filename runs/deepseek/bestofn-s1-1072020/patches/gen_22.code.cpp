FieldBase::FieldBase(const FieldBase &field)
{
    std::memmove(&values, &field.values, sizeof(values) + sizeof(stringIndexes));
}
