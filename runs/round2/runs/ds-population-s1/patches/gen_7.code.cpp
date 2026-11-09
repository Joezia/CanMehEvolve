FieldBase::FieldBase(const FieldBase &field)
    : values(std::move(const_cast<FieldBase&>(field).values)),
      stringIndexes(std::move(const_cast<FieldBase&>(field).stringIndexes))
{
}
