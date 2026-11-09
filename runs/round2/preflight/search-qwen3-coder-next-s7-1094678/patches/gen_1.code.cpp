FieldBase::FieldBase(const FieldBase &field)
{
    values = std::move(field.values);
    stringIndexes = std::move(field.stringIndexes);
}
